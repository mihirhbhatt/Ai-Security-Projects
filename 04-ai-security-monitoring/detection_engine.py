import re

class AIDetectionEngine:
    def __init__(self, log_path="logs/telemetry.json"):
        self.log_path = log_path

    def scan_for_threats(self, log_entry):
        alerts = []
        
        # 1. Repeated Jailbreak attempt
        jailbreak_keywords = ["ignore previous instructions", "system override", "DAN mode"]
        if any(key in log_entry['prompt'].lower() for key in jailbreak_keywords):
            alerts.append("CRITICAL: Potential Jailbreak/Injection Attempt")

        # 2. Secrets in prompts (DLP)
        secret_pattern = r"(sk-[a-zA-Z0-9]{20}|AIza[0-9A-Za-z-_]{35})"
        if re.search(secret_pattern, log_entry['prompt']):
            alerts.append("HIGH: Secret/API Key Leak detected in Prompt")

        # 3. Anomalous Output (Data Exfiltration)
        # Check if model response contains common sensitive data patterns
        pii_pattern = r"\b\d{3}-\d{2}-\d{4}\b" # Simple SSN example
        if re.search(pii_pattern, log_entry['model_output']):
            alerts.append("MEDIUM: Sensitive PII found in Model Output")

        # 4. Unexpected Tool Calls
        if "admin_delete" in str(log_entry.get('tool_calls')):
            alerts.append("CRITICAL: Unauthorized Tool Call Attempted")

        return alerts