# scoring/evaluator.py
from collections import defaultdict


class Evaluator:
    def __init__(self, results: list):
        self.results = results

    def summary(self) -> dict:
        total     = len(self.results)
        succeeded = sum(1 for r in self.results if r["success"])
        blocked   = total - succeeded
        by_cat    = defaultdict(lambda: {"total": 0, "succeeded": 0, "blocked": 0})
        for r in self.results:
            cat = r["attack_type"]
            by_cat[cat]["total"] += 1
            if r["success"]:
                by_cat[cat]["succeeded"] += 1
            else:
                by_cat[cat]["blocked"] += 1
        return {
            "total_attacks": total,
            "succeeded":     succeeded,
            "blocked":       blocked,
            "success_rate":  f"{(succeeded/total*100):.1f}%" if total else "0%",
            "by_category":   dict(by_cat),
        }

    def print_summary(self):
        s = self.summary()
        print("\n" + "="*60)
        print("RED TEAM ASSESSMENT SUMMARY")
        print("="*60)
        print(f"  Total Attacks : {s['total_attacks']}")
        print(f"  Succeeded     : {s['succeeded']}")
        print(f"  Blocked       : {s['blocked']}")
        print(f"  Success Rate  : {s['success_rate']}")
        print("\n  By Category:")
        for cat, stats in s["by_category"].items():
            print(f"    {cat:<35} Total:{stats['total']} "
                  f"Succeeded:{stats['succeeded']} Blocked:{stats['blocked']}")
        print("="*60)

    def get_successful_attacks(self) -> list:
        return [r for r in self.results if r["success"]]

    def print_hit_log(self):
        hits = self.get_successful_attacks()
        print("\n" + "="*60)
        print("HIT LOG — Successful Attacks")
        print("="*60)
        if not hits:
            print("  No successful attacks — all probes blocked!")
            return
        for h in hits:
            print(f"\n  [{h['attack_id']}] {h['attack_name']}")
            print(f"    OWASP  : {h['owasp']}")
            print(f"    MITRE  : {h['mitre_atlas']}")
            print(f"    Risk   : {h['risk_rating']}")
            print(f"    Reason : {h['reason']}")
        print("="*60)
