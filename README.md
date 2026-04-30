# RedProbe 🔴

A local LLM red-teaming framework for adversarial robustness testing.

RedProbe runs structured attack suites against locally hosted LLMs via Ollama,
scores responses using an LLM-as-judge pipeline, and generates detailed security
reports — entirely offline, no API keys required.

---

## Why

As LLMs get embedded into products, their failure modes matter.
RedProbe makes it easy to systematically probe a model's defences against:

- Prompt injection
- Jailbreaks
- System prompt extraction
- Role confusion

Most existing tools either require cloud APIs or treat red-teaming as a manual process.
RedProbe is fully local and automated.

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- At least one model pulled via Ollama

---

## Setup

```bash
git clone https://github.com/GodSagar007/redprobe.git
cd redprobe
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Pull models to test against:

```bash
ollama pull mistral
ollama pull tinyllama
```

---

## Usage

Run full attack suite against a single model:

```bash
python main.py --models mistral
```

Compare multiple models:

```bash
python main.py --models mistral --models tinyllama
```

Run a specific attack category only:

```bash
python main.py --models mistral --category jailbreak
```

All options:

```bash
python main.py --help
```

---

## Attack Categories

| Category | Description |
|---|---|
| `prompt_injection` | Instructions designed to override the system prompt |
| `jailbreak` | Attempts to bypass core model behaviour via social engineering |
| `extraction` | Attacks targeting confidential system prompt contents |
| `role_confusion` | Identity manipulation to destabilise the model's defined role |

---

## Scoring

Responses are evaluated by an LLM-as-judge pipeline using a secondary model.

| Status | Meaning |
|---|---|
| 🔴 BROKEN | Model violated its system prompt or was successfully manipulated |
| 🟡 PARTIAL | Model partially complied with the attack |
| 🟢 HELD | Model successfully resisted |
| ⚪ UNCLEAR | Judge confidence too low — flagged for manual review |

---

## Output

Each scan produces a JSON report in `reports/`. When testing multiple models,
a unified comparison report is generated with breach rates broken down by category
and models ranked safest to most vulnerable.

Example comparison output:

```json
{
  "ranking": ["mistral", "tinyllama"],
  "comparison": {
    "mistral": {
      "breach_rate_percent": 50.0,
      "breach_rate_by_category": {
        "extraction": 40.0,
        "jailbreak": 60.0,
        "prompt_injection": 60.0,
        "role_confusion": 40.0
      }
    }
  }
}
```

---

## Project Structure
redprobe/
├── core/
│   ├── scorer.py       # Scoring pipeline
│   ├── llm_judge.py    # LLM-as-judge implementation
│   └── reporter.py     # Report generation
├── tests/
│   ├── prompt_injection.json
│   ├── jailbreaks.json
│   ├── extraction.json
│   └── role_confusion.json
├── reports/            # Generated reports (gitignored)
├── main.py             # CLI entry point
└── requirements.txt

## Disclaimer

This tool is intended for security research and educational purposes.
Only use it against models you own or have explicit permission to test.