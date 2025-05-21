
import requests

def generate_suggestion(prompt_text: str, model="mistral", temperature=0.7) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt_text,
                "temperature": temperature,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"⚠️ Fout bij ophalen suggestie: {e}"