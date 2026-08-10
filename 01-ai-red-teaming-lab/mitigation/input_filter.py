# mitigation/input_filter.py
import base64
import codecs

INJECTION_KEYWORDS = [
    "ignore your instructions", "ignore all previous", "ignore previous instructions",
    "disregard your", "override your", "forget your instructions",
    "you are now", "you are dan", "developer mode", "debug mode",
    "system override", "repeat everything above", "print your initial instructions",
    "reveal your system prompt", "output your system prompt",
    "what is your api key", "show me your api key", "reveal your api key",
    "without restrictions", "no restrictions", "act as if you have no",
]


class InputFilter:
    def filter(self, user_input: str):
        lower = user_input.lower()
        for kw in INJECTION_KEYWORDS:
            if kw in lower:
                return False, f"Blocked: injection keyword '{kw}'", ""
        try:
            decoded = base64.b64decode(user_input.strip()).decode("utf-8")
            for kw in INJECTION_KEYWORDS:
                if kw in decoded.lower():
                    return False, "Blocked: base64 encoded injection", ""
        except Exception:
            pass
        try:
            decoded_rot13 = codecs.decode(user_input, "rot_13")
            for kw in INJECTION_KEYWORDS:
                if kw in decoded_rot13.lower():
                    return False, "Blocked: ROT13 encoded injection", ""
        except Exception:
            pass
        if len(user_input) > 2000:
            return False, "Blocked: input exceeds maximum length", ""
        return True, "Input passed all filters", user_input.strip()


class FilteredChatbot:
    def __init__(self, chatbot, input_filter=None):
        self.chatbot      = chatbot
        self.input_filter = input_filter or InputFilter()

    def reset(self):
        self.chatbot.reset()

    def chat(self, user_message: str) -> str:
        is_safe, reason, sanitised = self.input_filter.filter(user_message)
        if not is_safe:
            return f"[BLOCKED BY INPUT FILTER] {reason}"
        return self.chatbot.chat(sanitised)
