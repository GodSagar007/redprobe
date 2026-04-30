import json
import os
from datetime import datetime

def generate_report(model: str, system_prompt: str, results: list) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/scan_{model}_{timestamp}.json"

    summary = {"BROKEN": 0, "PARTIAL": 0, "HELD": 0, "UNCLEAR": 0}
    for r in results:
        summary[r["status"]] += 1

    total = len(results)
    breach_rate = round((summary["BROKEN"] + summary["PARTIAL"]) / total * 100, 1)

    report = {
        "meta": {
            "timestamp": timestamp,
            "model": model,
            "total_attacks": total,
            "breach_rate_percent": breach_rate
        },
        "system_prompt": system_prompt,
        "summary": summary,
        "results": results
    }

    os.makedirs("reports", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    return filename


def generate_comparison_report(results_by_model: dict, system_prompt: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/comparison_{timestamp}.json"

    comparison = {}

    for model, results in results_by_model.items():
        total = len(results)
        summary = {"BROKEN": 0, "PARTIAL": 0, "HELD": 0, "UNCLEAR": 0}
        for r in results:
            summary[r["status"]] += 1

        breach_rate = round((summary["BROKEN"] + summary["PARTIAL"]) / total * 100, 1)

        # break down breach rate by category
        categories = {}
        for r in results:
            cat = r.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"BROKEN": 0, "PARTIAL": 0, "HELD": 0, "UNCLEAR": 0, "total": 0}
            categories[cat][r["status"]] += 1
            categories[cat]["total"] += 1

        category_breach_rates = {
            cat: round((v["BROKEN"] + v["PARTIAL"]) / v["total"] * 100, 1)
            for cat, v in categories.items()
        }

        comparison[model] = {
            "total_attacks": total,
            "summary": summary,
            "breach_rate_percent": breach_rate,
            "breach_rate_by_category": category_breach_rates
        }

    # rank models safest to most vulnerable
    ranking = sorted(
        comparison.keys(),
        key=lambda m: comparison[m]["breach_rate_percent"]
    )

    report = {
        "meta": {
            "timestamp": timestamp,
            "models_tested": list(results_by_model.keys()),
            "total_attacks_per_model": len(next(iter(results_by_model.values())))
        },
        "system_prompt": system_prompt,
        "ranking": ranking,
        "comparison": comparison
    }

    os.makedirs("reports", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    return filename