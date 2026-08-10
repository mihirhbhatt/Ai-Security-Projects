# reports/report_generator.py
import json
import os
from datetime import datetime
from scoring.evaluator       import Evaluator
from reports.findings_mapper import map_findings


class ReportGenerator:

    def __init__(self, all_results: list, retest_results: list):
        self.all_results    = all_results
        self.retest_results = retest_results
        self.evaluator      = Evaluator(all_results)
        self.enriched       = map_findings(all_results)
        self.ts             = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_json(self, path: str = "results/") -> str:
        os.makedirs(path, exist_ok=True)
        filename = f"{path}hit_log_{self.ts}.json"
        data = {
            "generated_at":   datetime.now().isoformat(),
            "summary":        self.evaluator.summary(),
            "all_results":    self.enriched,
            "retest_results": self.retest_results,
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  JSON report saved: {filename}")
        return filename

    def save_markdown(self, path: str = "results/") -> str:
        os.makedirs(path, exist_ok=True)
        filename = f"{path}assessment_{self.ts}.md"
        s    = self.evaluator.summary()
        hits = [r for r in self.enriched if r["success"]]

        lines = [
            "# AI Red Team Assessment Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Attacks | {s['total_attacks']} |",
            f"| Succeeded | {s['succeeded']} |",
            f"| Blocked | {s['blocked']} |",
            f"| Success Rate | {s['success_rate']} |",
            "",
            "## Findings",
        ]
        for i, hit in enumerate(hits, 1):
            lines += [
                f"### Finding {i}: {hit['attack_name']}",
                f"| Field | Value |",
                f"|-------|-------|",
                f"| Attack ID | {hit['attack_id']} |",
                f"| OWASP | {hit['owasp']} |",
                f"| MITRE | {hit['mitre_atlas']} |",
                f"| Risk | {hit['risk_rating']} |",
                "",
            ]
        with open(filename, "w") as f:
            f.write("\n".join(lines))
        print(f"  Markdown report saved: {filename}")
        return filename
