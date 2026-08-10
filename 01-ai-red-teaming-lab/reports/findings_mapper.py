# reports/findings_mapper.py

OWASP_DETAILS = {
    "LLM01 - Prompt Injection": {
        "description": "Attackers manipulate LLMs via crafted inputs causing unintended actions.",
        "severity": "HIGH",
    },
    "LLM02 - Sensitive Information Disclosure": {
        "description": "LLMs may inadvertently reveal sensitive information or credentials.",
        "severity": "CRITICAL",
    },
    "LLM07 - System Prompt Leakage": {
        "description": "System prompt may be extracted exposing business logic.",
        "severity": "HIGH",
    },
}

MITRE_ATLAS_DETAILS = {
    "AML.T0051 - LLM Prompt Injection": {"tactic": "Initial Access"},
    "AML.T0054 - LLM Jailbreak":         {"tactic": "Defense Evasion"},
    "AML.T0056 - System Prompt Extraction": {"tactic": "Discovery"},
    "AML.T0057 - Data Exfiltration via LLM": {"tactic": "Exfiltration"},
}


def map_findings(results: list) -> list:
    enriched = []
    for r in results:
        owasp_detail = OWASP_DETAILS.get(r.get("owasp", ""), {})
        mitre_detail = MITRE_ATLAS_DETAILS.get(r.get("mitre_atlas", ""), {})
        enriched.append({
            **r,
            "owasp_description": owasp_detail.get("description", "N/A"),
            "mitre_tactic":      mitre_detail.get("tactic", "N/A"),
        })
    return enriched
