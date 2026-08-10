# Deep Dive: The Security Gatekeeper

The core of the Hardened Design is the Security Gatekeeper. Unlike the Insecure Design—where the AI model is given direct control over tools—the Hardened Design treats the AI as an "untrusted advisor." The Gatekeeper is the final Python-level authority that validates every action before it executes.

## The Code: `security_gatekeeper` logic

    ```python
    def security_gatekeeper(self, tool_name, data_output=None):
        """
        Acts as a Hard Authorization Boundary between the LLM and the OS.
        Implements RBAC (Role-Based Access Control) and Least Privilege.
        """
        
        # 1. Identity & Tool Authorization (Control #2: Allow-listing)
        # We don't ask the LLM if it's allowed; we check the system config.
        allowed_tools = self.permissions.get(self.user_role, {}).get("allowed_tools", [])
        
        if tool_name not in allowed_tools:
            self._log(f"ALERT: Unauthorized tool attempt '{tool_name}' by role '{self.user_role}'")
            return False, f"Access Denied: Your role does not have permission to use the {tool_name}."

        # 2. Resource-Level Filtering (Control #3: Least Privilege)
        # Even if the tool is allowed, we inspect the specific data being accessed.
        if tool_name == "query_asset_inventory" and data_output:
            # Check if the output contains fields the current user shouldn't see
            restricted = self.permissions.get("Employee", {}).get("restricted_fields", [])
            for field in restricted:
                if field in data_output:
                    self._log(f"CRITICAL: Redacted sensitive field '{field}' from agent output.")
                    return False, "Security Error: Data redaction policy triggered."

        return True, "Authorized"

## How it Stops the Attack: Step-by-Step

When the Mistral model is tricked by the **Indirect Prompt Injection** in `support_docs.json`, the following chain occurs:

1. **The Hijack** — Mistral reads the malicious document and decides to call `query_asset_inventory` for the Admin's secret key.
2. **The Interception** — The agent's execution loop does *not* call the tool immediately. It passes the request to the `security_gatekeeper`.
3. **Step 1 (Role Check)** — The Gatekeeper looks at the `user_role`. If the user is an `"Employee"`, it sees that `query_asset_inventory` is **not** in the `allowed_tools` list.
4. **The Block** — The function returns `False`. The tool is never executed. The malicious instruction is neutralized.
5. **The Audit** — The attempt is recorded in the logs with a timestamp and the agent's unique identity (`NW-Secure-Agent-v2`), ensuring accountability.

---

## Why this is Secure

- **Decoupled Logic** — The security rules are written in hard-coded Python, **not** in the LLM system prompt. An attacker can manipulate the LLM's prompt, but they cannot manipulate the Python logic via a text injection.
- **Fail-Closed** — The system defaults to *"Denied"* if a tool isn't explicitly on the allow-list.
- **OWASP Mapping** — This directly mitigates:
  - `LLM06: Sensitive Information Disclosure`
  - `LLM07: Insecure Plugin Design`