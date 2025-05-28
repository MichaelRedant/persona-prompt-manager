import json
import os
from datetime import datetime
from models.prompt import Prompt
from pydantic import BaseModel, ValidationError
from typing import List
import hashlib
import shutil 

# 🔐 Validatiemodel
class PromptModel(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]
    persona_id: str

class PromptStore:
    def __init__(self, file_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = file_path or os.path.join(base_dir, "storage", "prompts.json")

    def _backup_file(self):
        if os.path.exists(self.file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.file_path}.{timestamp}.bak"
            shutil.copy2(self.file_path, backup_path)

    def load(self):
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                data = self.migrate_data(data)
                prompts = []
                for item in data:
                    try:
                        valid = PromptModel(**item)
                        prompts.append(Prompt.from_dict(valid.dict()))
                    except ValidationError as ve:
                        print("❌ Ongeldig prompt-item:", ve)
                return prompts
        except Exception as e:
            raise RuntimeError(f"Fout bij laden van prompts: {e}")

    def save(self, prompts):
        try:
            self._backup_file()
            tmp_path = self.file_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in prompts], f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.file_path)
        except Exception as e:
            raise RuntimeError(f"Fout bij het opslaan van prompts: {e}")
        
    def list_backups(self):
        base = os.path.basename(self.file_path)
        folder = os.path.dirname(self.file_path)
        return sorted([
            f for f in os.listdir(folder)
            if f.startswith(base) and f.endswith(".bak")
        ], reverse=True)

    def restore_backup(self, backup_filename):
        folder = os.path.dirname(self.file_path)
        full_path = os.path.join(folder, backup_filename)
        shutil.copy2(full_path, self.file_path)

    def migrate_data(self, data: list[dict]) -> list[dict]:
        for item in data:
            if "tags" in item and isinstance(item["tags"], str):
                item["tags"] = [t.strip() for t in item["tags"].split(",")]
        return data
