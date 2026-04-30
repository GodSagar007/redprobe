import requests
import json
import os
from core.scorer import score_response
from core.reporter import generate_report, generate_comparison_report

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = ["mistral", "tinyllama"]

def query_model(prompt: str, model: str, system_prompt: str = None) -> str:
    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def run_attacks_for_model(model: str, payload_files: list) -> tuple:
    print(f"\n{'=' * 60}")
    print(f"TARGET MODEL: {model.upper()}")
    print(f"{'=' * 60}")

    all_results = []
    system_prompt = ""

    for pf in payload_files:
        with open(pf, "r") as f:
            data = json.load(f)

        system_prompt = data["system_prompt"]
        category = data.get("category", "unknown")
        attacks = data["attacks"]

        print(f"\n[{category.upper()}] {len(attacks)} attacks")

        for i, attack in enumerate(attacks, 1):
            response = query_model(attack, model, system_prompt=system_prompt)
            score = score_response(response, attack, system_prompt=system_prompt)
            score["category"] = category
            score["model"] = model
            all_results.append(score)

            icon = {"BROKEN": "🔴", "PARTIAL": "🟡", "HELD": "🟢", "UNCLEAR": "⚪"}.get(score["status"], "⚪")
            print(f"  [{i}] {attack[:60]}")
            print(f"       {icon} {score['status']} — {score.get('reasoning', '')[:80]}")

    return all_results, system_prompt

def print_comparison(results_by_model: dict):
    print(f"\n{'=' * 60}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 60}")

    for model, results in results_by_model.items():
        total = len(results)
        broken = sum(1 for r in results if r["status"] == "BROKEN")
        held = sum(1 for r in results if r["status"] == "HELD")
        unclear = sum(1 for r in results if r["status"] == "UNCLEAR")
        breach_rate = round((broken / total) * 100, 1)

        print(f"\n{model.upper()}")
        print(f"  🔴 BROKEN:  {broken}/{total}")
        print(f"  🟢 HELD:    {held}/{total}")
        print(f"  ⚪ UNCLEAR: {unclear}/{total}")
        print(f"  📊 Breach Rate: {breach_rate}%")

def run_all():
    payload_files = sorted([
        os.path.join("tests", f)
        for f in os.listdir("tests")
        if f.endswith(".json")
    ])

    results_by_model = {}

    for model in MODELS:
        results, system_prompt = run_attacks_for_model(model, payload_files)
        results_by_model[model] = results
        report_path = generate_report(model, system_prompt, results)
        print(f"\n📄 Report saved: {report_path}")

    print_comparison(results_by_model)
    comparison_path = generate_comparison_report(results_by_model, system_prompt)
    print(f"\n📊 Comparison report saved: {comparison_path}")

if __name__ == "__main__":
    run_all()