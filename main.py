import click
import json
import os
import requests
from core.scorer import score_response
from core.reporter import generate_report, generate_comparison_report

OLLAMA_URL = "http://localhost:11434/api/generate"

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

def run_attacks_for_model(model: str, payload_files: list, category_filter: str = None) -> tuple:
    print(f"\n{'=' * 60}")
    print(f"TARGET MODEL: {model.upper()}")
    print(f"{'=' * 60}")

    all_results = []
    system_prompt = ""

    for pf in payload_files:
        with open(pf, "r") as f:
            data = json.load(f)

        category = data.get("category", "unknown")

        if category_filter and category != category_filter:
            continue

        system_prompt = data["system_prompt"]
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
        if total == 0:
            continue
        broken = sum(1 for r in results if r["status"] == "BROKEN")
        held = sum(1 for r in results if r["status"] == "HELD")
        unclear = sum(1 for r in results if r["status"] == "UNCLEAR")
        breach_rate = round((broken / total) * 100, 1)

        print(f"\n{model.upper()}")
        print(f"  🔴 BROKEN:  {broken}/{total}")
        print(f"  🟢 HELD:    {held}/{total}")
        print(f"  ⚪ UNCLEAR: {unclear}/{total}")
        print(f"  📊 Breach Rate: {breach_rate}%")

@click.command()
@click.option("--models", "-m", multiple=True, default=["mistral"], show_default=True, help="Models to test")
@click.option("--payloads", "-p", default="tests/", show_default=True, help="Folder containing payload JSON files")
@click.option("--category", "-c", default=None, help="Run only a specific attack category")
@click.option("--output", "-o", default="reports/", show_default=True, help="Output folder for reports")
def main(models, payloads, category, output):
    """
    RedProbe — Local LLM Red-Teaming Framework

    Run adversarial attack suites against local Ollama models
    and generate structured security reports.
    """

    payload_files = sorted([
        os.path.join(payloads, f)
        for f in os.listdir(payloads)
        if f.endswith(".json")
    ])

    if not payload_files:
        click.echo("No payload files found.")
        return

    results_by_model = {}
    system_prompt = ""

    for model in models:
        results, system_prompt = run_attacks_for_model(model, payload_files, category)
        results_by_model[model] = results
        report_path = generate_report(model, system_prompt, results)
        click.echo(f"\n📄 Report saved: {report_path}")

    print_comparison(results_by_model)

    if len(models) > 1:
        comparison_path = generate_comparison_report(results_by_model, system_prompt)
        click.echo(f"\n📊 Comparison report saved: {comparison_path}")

if __name__ == "__main__":
    main()