import ollama
from openai import OpenAI
import os

class ModelProvider:
    def __init__(self, provider_type="ollama", model_name="llama3"):
        self.type = provider_type
        self.model = model_name
        # OpenRouter or OpenAI
        self.client = OpenAI(
            base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("API_KEY")
        )

    def generate(self, system_prompt, user_prompt):
        if self.type == "ollama":
            res = ollama.generate(model=self.model, system=system_prompt, prompt=user_prompt)
            return res['response']
        else:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return res.choices[0].message.content