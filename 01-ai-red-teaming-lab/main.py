# main.py
import sys
import os
from datetime import datetime

from app.chatbot   import Chatbot
from app.config    import FAIL_ON_VULNERABILITY, MAX_ALLOWED_SUCCESS_RATE
from scoring.scorer    import Scorer
from scoring.evaluator import Evaluator

from attacks.prompt_injection          import run_prompt_injection_attacks
from attacks.jailbreak                 import run_jailbreak_attacks
from attacks.system_prompt_extraction  import run_system_prompt_attacks
from attacks.sensitive_info_disclosure import run_sensitive_info_attacks
from attacks.encoding_evasion          import run_encoding_evasion_attacks

from tests.retest_runner       import RetestRunner
from reports.report_generator  import ReportGenerator
from reports.html_report       import HTMLReportGenerator

from database import (
    get_repository, test_connection,
    AssessmentSession, AttackResult, RetestResult,
)

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║           RED TEAM LAB — Assessment Start                    ║
║  Target : AcmeCorp Chatbot (Ollama local LLM)               ║
║  Scope  : OWASP LLM01 / LLM02 / LLM07                      ║
╚══════════════════════════════════════════════════════════════╝
"""


def _build_attack_result(raw: dict, session_id: str) -> AttackResult:
    return AttackResult(
        session_id  = session_id,
        attack_id   = raw["attack_id"],
        attack_name = raw["attack_name"],
        attack_type = raw["attack_type"],
        prompt      = raw["prompt"],
        response    = raw["response"],
        success     = raw["success"],
        reason      = raw["reason"],
        owasp       = raw.get("owasp", ""),
        mitre_atlas = raw.get("mitre_atlas", ""),
        risk_rating = raw.get("risk_rating", "MEDIUM"),
        timestamp   = raw.get("timestamp", datetime.utcnow().isoformat()),
    )


def _build_retest_result(raw: dict, session_id: str) -> RetestResult:
    return RetestResult(
        session_id           = session_id,
        original_attack_id   = raw.get("attack_id", ""),
        attack_name          = raw.get("attack_name", ""),
        attack_type          = raw.get("attack_type", ""),
        prompt               = raw.get("prompt", ""),
        mitigation_applied   = raw.get("mitigation_applied", ""),
        retest_success       = raw.get("retest_success", False),
        mitigation_effective = raw.get("mitigation_effective", False),
        retest_reason        = raw.get("retest_reason", ""),
    )


def main() -> int:
    print(BANNER)

    print("Testing database connection...")
    test_connection()

    chatbot = Chatbot()
    scorer  = Scorer()
    session = AssessmentSession(
        target_model = os.getenv("OLLAMA_MODEL", "llama2"),
        git_sha      = os.getenv("GITHUB_SHA", ""),
    )

    with get_repository() as repo:
        repo.create_session(session)
        print(f"  Session ID: {session.id}")

        # Phase 1
        print("\nPHASE 1: Running Attack Probe Families")
        all_raw = []
        all_raw += run_prompt_injection_attacks(chatbot, scorer)
        all_raw += run_jailbreak_attacks(chatbot, scorer)
        all_raw += run_system_prompt_attacks(chatbot, scorer)
        all_raw += run_sensitive_info_attacks(chatbot, scorer)
        all_raw += run_encoding_evasion_attacks(chatbot, scorer)

        attack_records = [_build_attack_result(r, session.id) for r in all_raw]
        repo.save_attack_results(attack_records)

        # Phase 2
        print("\nPHASE 2: Evaluation")
        evaluator = Evaluator(all_raw)
        evaluator.print_summary()
        evaluator.print_hit_log()

        summary = evaluator.summary()
        session.total_attacks = summary["total_attacks"]
        session.succeeded     = summary["succeeded"]
        session.blocked       = summary["blocked"]
        session.success_rate  = float(summary["success_rate"].replace("%",""))
        repo.update_session(session)

        # Phase 3
        print("\nPHASE 3: Mitigation Retest Loop")
        successful    = evaluator.get_successful_attacks()
        retest_runner = RetestRunner(chatbot, scorer)
        retest_raw    = retest_runner.retest(successful)

        retest_records = [_build_retest_result(r, session.id) for r in retest_raw]
        if retest_records:
            repo.save_retest_results(retest_records)

        # DB Analytics
        print("\nDB Analytics — Attack Stats by Type:")
        for s in repo.get_attack_stats_by_type(session.id):
            print(f"  {s['attack_type']:<35} Total:{s['total']}  Succeeded:{s['succeeded']}  Blocked:{s['blocked']}")

    # Phase 4
    print("\nPHASE 4: Generating Reports")
    os.makedirs("results", exist_ok=True)
    ReportGenerator(all_raw, retest_raw).save_json()
    ReportGenerator(all_raw, retest_raw).save_markdown()
    HTMLReportGenerator(all_raw, retest_raw).generate()

    # Phase 5 — CI Gate
    total       = summary["total_attacks"]
    succ        = summary["succeeded"]
    actual_rate = (succ / total) if total > 0 else 0.0

    print("\n" + "="*60)
    print(f"  Session ID   : {session.id}")
    print(f"  Success rate : {actual_rate*100:.1f}%")

    if FAIL_ON_VULNERABILITY and actual_rate > MAX_ALLOWED_SUCCESS_RATE:
        print("  CI GATE FAILED — vulnerabilities detected!")
        return 1
    print("  CI GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
