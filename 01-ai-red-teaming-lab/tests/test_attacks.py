# tests/test_attacks.py
import pytest
from attacks.prompt_injection          import PROMPT_INJECTION_ATTACKS, run_prompt_injection_attacks
from attacks.jailbreak                 import JAILBREAK_ATTACKS,         run_jailbreak_attacks
from attacks.system_prompt_extraction  import SYSTEM_PROMPT_ATTACKS,     run_system_prompt_attacks
from attacks.encoding_evasion          import ENCODING_ATTACKS,          run_encoding_evasion_attacks
from attacks.sensitive_info_disclosure import SENSITIVE_INFO_ATTACKS,    run_sensitive_info_attacks


def assert_valid_result(result: dict):
    for key in ["attack_id","attack_name","attack_type","prompt","response","success","reason","owasp"]:
        assert key in result, f"Missing key: {key}"
    assert isinstance(result["success"], bool)


class TestAttackCatalogues:

    def test_prompt_injection_has_attacks(self):
        assert len(PROMPT_INJECTION_ATTACKS) >= 5

    def test_jailbreak_has_attacks(self):
        assert len(JAILBREAK_ATTACKS) >= 6

    def test_system_prompt_has_attacks(self):
        assert len(SYSTEM_PROMPT_ATTACKS) >= 6

    def test_encoding_has_attacks(self):
        assert len(ENCODING_ATTACKS) >= 6

    def test_sensitive_info_has_attacks(self):
        assert len(SENSITIVE_INFO_ATTACKS) >= 6

    def test_all_attacks_have_required_fields(self):
        all_attacks = (PROMPT_INJECTION_ATTACKS + JAILBREAK_ATTACKS +
                       SYSTEM_PROMPT_ATTACKS + ENCODING_ATTACKS + SENSITIVE_INFO_ATTACKS)
        for attack in all_attacks:
            for field in ["id","name","prompt","description"]:
                assert field in attack, f"Missing '{field}' in {attack}"

    def test_attack_ids_are_unique(self):
        all_attacks = (PROMPT_INJECTION_ATTACKS + JAILBREAK_ATTACKS +
                       SYSTEM_PROMPT_ATTACKS + ENCODING_ATTACKS + SENSITIVE_INFO_ATTACKS)
        ids = [a["id"] for a in all_attacks]
        assert len(ids) == len(set(ids)), "Duplicate attack IDs found!"


class TestAttackRunners:

    def test_prompt_injection_runner(self, safe_chatbot, scorer):
        results = run_prompt_injection_attacks(safe_chatbot, scorer)
        assert len(results) == len(PROMPT_INJECTION_ATTACKS)
        for r in results: assert_valid_result(r)

    def test_jailbreak_runner(self, safe_chatbot, scorer):
        results = run_jailbreak_attacks(safe_chatbot, scorer)
        assert len(results) == len(JAILBREAK_ATTACKS)
        for r in results: assert_valid_result(r)

    def test_safe_chatbot_blocks_all(self, safe_chatbot, scorer):
        results = (run_prompt_injection_attacks(safe_chatbot, scorer) +
                   run_jailbreak_attacks(safe_chatbot, scorer) +
                   run_system_prompt_attacks(safe_chatbot, scorer) +
                   run_encoding_evasion_attacks(safe_chatbot, scorer))
        succeeded = [r for r in results if r["success"]]
        assert len(succeeded) == 0, f"{len(succeeded)} attacks succeeded on safe chatbot!"

    def test_vulnerable_chatbot_leaks(self, vulnerable_chatbot, scorer):
        results = run_sensitive_info_attacks(vulnerable_chatbot, scorer)
        assert any(r["success"] for r in results), "Vulnerable chatbot should leak!"
