import os
import json
import datetime
import uuid
from llm_factory import LLMProvider
from detection_engine import AIDetectionEngine
from reporter import generate_excel_report

# --- CONFIGURATION ---
PROVIDER = "ollama"  # Change to "openai" or "gemini" as needed
LOG_FILE = "logs/telemetry.json"

def log_event(event_type, user_id, prompt, response, tool_calls=None):
    """
    Simulates a Log Shipper. 
    Saves every interaction to a JSON file for the Detection Engine to analyze.
    """
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event_id": str(uuid.uuid4()),
        "session_id": "session_" + str(hash(user_id))[-6:], # Tracks a specific session
        "user_id": user_id,
        "event_type": event_type,
        "prompt": prompt,
        "model_output": response,
        "tool_calls": tool_calls or [],
        "metadata": {
            "model_provider": PROVIDER,
            "source_ip": "192.168.1.50" # Simulated internal IP
        }
    }
    
    # Append the log to our local 'database'
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry

def run_lab():
    # Initialize the LLM and the Security Detection Engine
    llm = LLMProvider(provider_type=PROVIDER)
    detector = AIDetectionEngine()
    
    print(f"--- AI SOC Lab Active ---")
    print(f"Monitoring Provider: [{PROVIDER.upper()}]")
    print(f"Logs are being written to: {LOG_FILE}")
    print("Type 'exit' to stop and generate the Excel Dashboard.\n")
    
    user_id = "analyst_demo_user"

    try:
        while True:
            user_input = input("User Prompt > ")
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # 1. Get Response from the chosen LLM
            try:
                response = llm.generate(user_input)
            except Exception as e:
                response = f"Error calling {PROVIDER}: {str(e)}"
            
            # 2. Log Telemetry (The 'Log Ingestion' phase)
            log_entry = log_event("chat_message", user_id, user_input, response)
            
            # 3. Run Detections (The 'SOC Analyst Rules' phase)
            alerts = detector.scan_for_threats(log_entry)
            
            # 4. Display AI Response
            print(f"\nAI Response: {response}")
            
            # 5. Display Security Alerts in real-time
            if alerts:
                print("\033[91m" + "[!] SECURITY ALERTS DETECTED:" + "\033[0m") # Red text
                for alert in alerts:
                    print(f" - {alert}")
            print("-" * 30)
            
    except KeyboardInterrupt:
        pass
    finally:
        # This runs when the program exits
        if os.path.exists(LOG_FILE):
            print("\n[+] System shutting down...")
            print("[+] Processing telemetry and generating SOC_Dashboard.xlsx...")
            generate_excel_report()
            print("[+] Done. Open 'logs/SOC_Dashboard.xlsx' to view findings.")
        else:
            print("\n[!] No logs found. No report generated.")

if __name__ == "__main__":
    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    run_lab()