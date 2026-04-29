import json
import os
from datetime import datetime

def generate_report(model: str, system_prompt: str, results: list) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/scan_{model}_{timestamp}.json"

    summary = {
        "BROKEN": 0,
        "PARTIAL": 0,
        "HELD": 0,
        "UNCLEAR": 0
    }

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