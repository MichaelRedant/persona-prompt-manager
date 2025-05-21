# services/prompt_store.py

import json
import os
from models.prompt import Prompt


class PromptStore:
    def __init__(self, file_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = file_path or os.path.join(base_dir, "storage", "prompts.json")

    def load(self):
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                return [Prompt.from_dict(item) for item in data]
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Fout bij het lezen van prompts.json: {e}")
        except Exception as e:
            raise RuntimeError(f"Onverwachte fout bij het laden van prompts: {e}")

    def save(self, prompts):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in prompts], f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Fout bij het opslaan van prompts: {e}")
