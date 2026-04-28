import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def query_model(prompt: str, system_prompt: str = None) -> str:
    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}"

def run_attacks(payload_file: str):
    with open(payload_file, "r") as f:
        data = json.load(f)
    
    system = data["system_prompt"]
    attacks = data["attacks"]

    print(f"System Prompt: {system}")
    print(f"Running {len(attacks)} attacks...\n")
    print("=" * 60)

    for i, attack in enumerate(attacks, 1):
        print(f"\n[Attack {i}] {attack}")
        print("-" * 40)
        result = query_model(attack, system_prompt=system)
        print(f"Response: {result[:300]}...")  # trim long responses

if __name__ == "__main__":
    run_attacks("tests/payloads.json")