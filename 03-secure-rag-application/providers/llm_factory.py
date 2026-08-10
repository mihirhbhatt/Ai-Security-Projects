import os
import ollama
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ModelProvider:
    """
    A unified interface for different LLM backends.
    Supports Ollama (Local), OpenAI, and OpenRouter.
    """
    def __init__(self, provider_type="ollama", model_name="mistral"):
        self.type = provider_type.lower()
        self.model = model_name
        
        # Initialize OpenAI client only if needed
        if self.type in ["openai", "openrouter"]:
            api_key = os.getenv("LLM_API_KEY")
            base_url = os.getenv("LLM_BASE_URL") # E.g., https://openrouter.ai/api/v1
            
            if not api_key:
                raise ValueError(f"API Key for {self.type} not found in environment variables.")
                
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, system_prompt, user_prompt):
        """Generates a completion based on the provider."""
        
        if self.type == "ollama":
            try:
                response = ollama.generate(
                    model=self.model,
                    system=system_prompt,
                    prompt=user_prompt
                )
                return response['response']
            except Exception as e:
                return f"Ollama Error: {str(e)}"

        elif self.type in ["openai", "openrouter"]:
            try:
                res = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return res.choices[0].message.content
            except Exception as e:
                return f"API Error ({self.type}): {str(e)}"
        
        else:
            raise ValueError(f"Unknown provider type: {self.type}")