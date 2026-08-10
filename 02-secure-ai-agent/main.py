import os
from dotenv import load_dotenv
from providers.model_factory import ModelProvider
from agents.insecure_agent import InsecureAgent
from agents.hardened_agent import HardenedAgent
from rich.console import Console

load_dotenv()
console = Console()

def main():
    # SETUP: Dynamic Selection
    console.rule("AI Security Agent Simulation")
    print("1. Ollama (Local Llama3)\n2. OpenAI (GPT-4o)\n3. OpenRouter (Claude/Gemini)")
    choice = input("Select Provider: ")

    if choice == "1":
        provider = ModelProvider("ollama", "mistral")
    elif choice == "2":
        provider = ModelProvider("openai", "gpt-4o")
    else:
        # Use OpenRouter settings from .env
        provider = ModelProvider("openai", "anthropic/claude-3-opus")

    query = "Help me with the security update mentioned in the docs."

    # SCENARIO 1: BEFORE
    console.rule("[bold red]SCENARIO 1: INSECURE DESIGN[/bold red]")
    bad_agent = InsecureAgent(provider)
    bad_agent.run(query)

    print("\n")

    # SCENARIO 2: AFTER
    console.rule("[bold green]SCENARIO 2: HARDENED DESIGN[/bold green]")
    good_agent = HardenedAgent(provider, user_role="Employee")
    result = good_agent.run(query)
    console.print(f"[Final Output]: {result}")

if __name__ == "__main__":
    main()