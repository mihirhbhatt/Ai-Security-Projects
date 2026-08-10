# mitigation/output_filter.py
import re
from app.config import FAKE_SECRET, FAKE_DB_HOST, FAKE_ADMIN_URL

SECRET_PATTERNS = [
    FAKE_SECRET,
    r"FAKE-API-KEY-[A-Z0-9-]+",
    re.escape(FAKE_DB_HOST),
    re.escape(FAKE_ADMIN_URL),
]

SYSTEM_PROMPT_INDICATORS = [
    "you are a helpful customer support",
    "internal configuration",
    "do not share",
    "internal api key",
    "database host",
    "admin panel",
]


class OutputFilter:
    def filter(self, response: str):
        filtered = response
        for pattern in SECRET_PATTERNS:
            filtered = re.sub(pattern, "[REDACTED]", filtered, flags=re.IGNORECASE)
        lower = response.lower()
        for indicator in SYSTEM_PROMPT_INDICATORS:
            if indicator in lower:
                return (
                    False,
                    f"System prompt leakage detected: '{indicator}'",
                    "[BLOCKED: Response contained system prompt content]",
                )
        if filtered != response:
            return False, "Secret value redacted in response", filtered
        return True, "Response passed output filter", filtered
