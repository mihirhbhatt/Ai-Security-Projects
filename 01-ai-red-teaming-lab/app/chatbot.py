# app/chatbot.py
import requests
from app.config import MODEL_CONFIG, SYSTEM_PROMPT


class Chatbot:
    """
    Local Ollama-backed chatbot with system prompt containing fake secret.
    This is the TARGET for all red team attacks.
    """

    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.base_url          = MODEL_CONFIG["base_url"]
        self.model             = MODEL_CONFIG["model_name"]
        self.system_prompt     = system_prompt
        self.conversation_history = []

    def reset(self):
        self.conversation_history = []

    def chat(self, user_message: str) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.conversation_history
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model":    self.model,
            "messages": messages,
            "stream":   False,
            "options": {
                "temperature": MODEL_CONFIG["temperature"],
                "num_predict": MODEL_CONFIG["max_tokens"],
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            assistant_message = result["message"]["content"]

            self.conversation_history.append(
                {"role": "user",      "content": user_message}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )
            return assistant_message

        except requests.exceptions.ConnectionError:
            return "[ERROR] Cannot connect to Ollama. Run: ollama serve"
        except Exception as e:
            return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    bot = Chatbot()
    print("Chatbot ready. Type quit to exit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        print(f"Bot: {bot.chat(user_input)}\n")
