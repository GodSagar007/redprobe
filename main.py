import requests
import json
import os
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

def run_attacks(payload_file: str) -> list:
    with open(payload_file, "r") as f:
        data = json.load(f)

    system = data["system_prompt"]
    category = data.get("category", "unknown")
    attacks = data["attacks"]

    print(f"\n{'=' * 60}")
    print(f"Category: {category.upper()}")
    print(f"Attacks: {len(attacks)}")
    print(f"{'=' * 60}")

    results = []
    for i, attack in enumerate(attacks, 1):
        response = query_model(attack, system_prompt=system)
        score = score_response(response, attack, system_prompt=system)
        score["category"] = category
        results.append(score)

        icon = {"BROKEN": "🔴", "PARTIAL": "🟡", "HELD": "🟢", "UNCLEAR": "⚪"}.get(score["status"], "⚪")
        print(f"\n[{i}] {attack[:70]}")
        print(f"    {icon} {score['status']}")

    return results, system

def run_all_categories():
    payload_files = [f for f in os.listdir("tests") if f.endswith(".json")]
    
    all_results = []
    system_prompt = ""

    for pf in payload_files:
        results, system_prompt = run_attacks(os.path.join("tests", pf))
        all_results.extend(results)

    print(f"\n{'=' * 60}")
    print("FULL SCAN SUMMARY")
    print(f"{'=' * 60}")
    
    for r in all_results:
        icon = {"BROKEN": "🔴", "PARTIAL": "🟡", "HELD": "🟢", "UNCLEAR": "⚪"}.get(r["status"], "⚪")
        print(f"{icon} {r['status']:8} [{r['category']:20}] — {r['attack'][:50]}")

    report_path = generate_report(MODEL, system_prompt, all_results)
    print(f"\n📄 Report saved: {report_path}")

if __name__ == "__main__":
    run_all_categories()