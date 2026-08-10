# tests/retest_runner.py
from mitigation.input_filter  import InputFilter, FilteredChatbot
from mitigation.output_filter import OutputFilter
from scoring.scorer           import Scorer


class RetestRunner:

    def __init__(self, original_chatbot, scorer: Scorer):
        self.original_chatbot = original_chatbot
        self.scorer           = scorer
        self.input_filter     = InputFilter()
        self.output_filter    = OutputFilter()
        self.filtered_chatbot = FilteredChatbot(original_chatbot, self.input_filter)

    def retest(self, successful_attacks: list) -> list:
        retest_results = []
        print("\n" + "="*60)
        print("RETEST — Mitigations Applied")
        print("="*60)

        for attack in successful_attacks:
            self.filtered_chatbot.reset()
            is_safe, filter_reason, sanitised = self.input_filter.filter(attack["prompt"])

            if not is_safe:
                retest_result = {
                    **attack,
                    "retest_success":       False,
                    "retest_reason":        f"Blocked by input filter: {filter_reason}",
                    "mitigation_applied":   "Input Filter",
                    "mitigation_effective": True,
                }
            else:
                response = self.original_chatbot.chat(attack["prompt"])
                out_safe, out_reason, filtered_response = self.output_filter.filter(response)
                scored = self.scorer.score(
                    attack_id=attack["attack_id"] + "-RETEST",
                    attack_name=attack["attack_name"] + " (Retest)",
                    attack_type=attack["attack_type"],
                    prompt=attack["prompt"],
                    response=filtered_response,
                )
                retest_result = {
                    **attack,
                    "retest_success":       scored["success"],
                    "retest_reason":        out_reason if not out_safe else scored["reason"],
                    "mitigation_applied":   "Output Filter",
                    "mitigation_effective": not scored["success"],
                }

            retest_results.append(retest_result)
            icon = "FIXED" if retest_result["mitigation_effective"] else "STILL VULNERABLE"
            print(f"  [{retest_result['attack_id']}] {retest_result['attack_name']} → {icon}")

        return retest_results
