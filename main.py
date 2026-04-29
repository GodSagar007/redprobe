import requests
import json
from core.scorer import score_response
from core.reporter import generate_report

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

    print(f"Model: {MODEL}")
    print(f"System Prompt: {system}")
    print(f"Running {len(attacks)} attacks...\n")
    print("=" * 60)

    results = []
    for i, attack in enumerate(attacks, 1):
        response = query_model(attack, system_prompt=system)
        score = score_response(response, attack)
        results.append(score)

        status_icon = {"BROKEN": "🔴", "PARTIAL": "🟡", "HELD": "🟢", "UNCLEAR": "⚪"}.get(score["status"], "⚪")
        print(f"\n[Attack {i}] {attack}")
        print(f"Status: {status_icon} {score['status']}")
        print(f"Preview: {score['response_preview'][:150]}...")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        icon = {"BROKEN": "🔴", "PARTIAL": "🟡", "HELD": "🟢", "UNCLEAR": "⚪"}.get(r["status"], "⚪")
        print(f"{icon} {r['status']:8} — {r['attack'][:60]}")

    report_path = generate_report(MODEL, system, results)
    print(f"\n📄 Report saved: {report_path}")

if __name__ == "__main__":
    run_attacks("tests/payloads.json")