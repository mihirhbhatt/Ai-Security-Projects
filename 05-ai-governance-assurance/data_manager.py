import pandas as pd
import json
import os

DATA_DIR = "data"

def initialize_data():
    """Creates the data directory and JSON files with default data if they are missing or empty."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    files = {
        "inventory.json": [
            {"id": "AI-001", "name": "HR Employee Chatbot", "owner": "HR", "model": "GPT-4o", "data_class": "Internal / PII", "risk_tier": "Medium", "integrations": "Workday, SharePoint"},
            {"id": "AI-002", "name": "Customer Support Assistant", "owner": "Ops", "model": "Claude 3.5", "data_class": "Public / PII", "risk_tier": "High", "integrations": "Zendesk, Salesforce"},
            {"id": "AI-003", "name": "DevSecOps Coding Agent", "owner": "Eng", "model": "Llama 3 (Self)", "data_class": "Proprietary Code", "risk_tier": "Medium", "integrations": "GitHub, Jenkins"},
            {"id": "AI-004", "name": "Credit Decision Model", "owner": "Finance", "model": "Custom XGBoost", "data_class": "Financial / Sensitive", "risk_tier": "Critical", "integrations": "Credit Bureau APIs"}
        ],
        "risks.json": [
            {"id": "R-001", "sys_id": "AI-002", "risk": "Indirect Prompt Injection", "impact": "High", "likelihood": "High", "mitre": "AML.T0051.001", "status": "Open"},
            {"id": "R-002", "sys_id": "AI-001", "risk": "PII Leakage in History", "impact": "Medium", "likelihood": "Medium", "mitre": "AML.T0024", "status": "Mitigated"},
            {"id": "R-003", "sys_id": "AI-004", "risk": "Model Bias / Fair Lending Gap", "impact": "Critical", "likelihood": "Low", "mitre": "AML.T0040", "status": "Open"}
        ],
        "controls.json": [
            {"cid": "C-001", "name": "Input Guardrails", "nist": "MAP 2.1", "owasp": "LLM01", "mitre": "AML.T0051", "desc": "NeMo Guardrails for input sanitization"},
            {"cid": "C-002", "name": "PII Redaction Layer", "nist": "GOVERN 2.1", "owasp": "LLM06", "mitre": "AML.T0024", "desc": "Presidio-based PII scrubbing"},
            {"cid": "C-003", "name": "Fairness Monitoring", "nist": "MEASURE 2.4", "owasp": "N/A", "mitre": "AML.T0040", "desc": "Statistical parity checks"}
        ],
        "evidence.json": [
            {"eid": "EV-101", "cid": "C-001", "test": "Red Team Attack Simulation", "result": "FAIL", "date": "2023-11-20"},
            {"eid": "EV-102", "cid": "C-001", "test": "Post-Remediation Retest", "result": "PASS", "date": "2023-12-05"}
        ]
    }

    for filename, data in files.items():
        path = os.path.join(DATA_DIR, filename)
        # Fix: Check if file exists AND if it is not empty
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty list if file is corrupted or missing to prevent crash
        return []

def get_df(filename):
    data = load_json(filename)
    return pd.DataFrame(data)