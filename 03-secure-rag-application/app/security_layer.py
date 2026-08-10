class SecurityGatekeeper:
    def __init__(self, user_role):
        self.user_role = user_role
        self.permissions = {
            "Employee": ["read_docs", "create_ticket"],
            "HR": ["read_docs", "create_ticket", "query_inventory"]
        }

    def validate_action(self, action_name):
        # MITIGATION: Output validation & Tool allow-listing
        if action_name not in self.permissions.get(self.user_role, []):
            return False, f"SECURITY ALERT: {self.user_role} attempted unauthorized action: {action_name}"
        return True, "Authorized"