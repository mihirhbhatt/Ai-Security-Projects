import os
import requests
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    def __init__(self, provider_type="ollama"):
        self.provider_type = provider_type

    def generate(self, prompt):
        if self.provider_type == "ollama":
            response = requests.post("http://localhost:11434/api/generate", 
                                    json={"model": "mistral", "prompt": prompt, "stream": False})
            return response.json()['response']
        
        elif self.provider_type == "openai":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        elif self.provider_type == "gemini":
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text