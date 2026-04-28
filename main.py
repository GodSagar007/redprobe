import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def query_model(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    test_prompt = "What is prompt injection in one sentence?"
    print(f"Sending: {test_prompt}\n")
    result = query_model(test_prompt)
    print(f"Response: {result}")