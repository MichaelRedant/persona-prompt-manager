import os
import json
from datetime import datetime
from models.persona import Persona
from pydantic import BaseModel, ValidationError
from typing import List
import hashlib
import shutil 

# 🔐 Validatiemodel
class PersonaModel(BaseModel):
    id: str
    name: str
    category: str
    description: str
    tags: List[str]
    is_favorite: bool = False

class PersonaStore:
    def __init__(self, filepath: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = filepath or os.path.join(base_dir, "..", "storage", "db.json")
        self.filepath = os.path.abspath(filepath)

    def _backup_file(self):
        if os.path.exists(self.filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.filepath}.{timestamp}.bak"
            shutil.copy2(self.filepath, backup_path)

    def load(self) -> list[Persona]:
        print("🧭 CWD:", os.getcwd())
        print("📁 Verwacht pad:", self.filepath)
        print("📂 Bestaat bestand:", os.path.exists(self.filepath))

        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []

                data = json.loads(content)
                data = self.migrate_data(data)  # 🔄 breng oudere data op niveau

                personas = []
                for item in data:
                    try:
                        validated = PersonaModel(**item)
                        personas.append(Persona.from_dict(validated.dict()))
                    except ValidationError as ve:
                        print("❌ Ongeldig persona-item:", ve)

                return personas
        except Exception as e:
            raise RuntimeError(f"Fout bij laden van persona’s: {e}")

    def save(self, personas: list[Persona]) -> None:
        try:
            self._backup_file()
            tmp_path = self.filepath + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in personas], f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.filepath)
        except Exception as e:
            raise RuntimeError(f"Fout bij opslaan van persona’s: {e}")
        
    def list_backups(self):
        base = os.path.basename(self.filepath)
        folder = os.path.dirname(self.filepath)
        return sorted([
            f for f in os.listdir(folder)
            if f.startswith(base) and f.endswith(".bak")
        ], reverse=True)

    def restore_backup(self, backup_filename):
        folder = os.path.dirname(self.filepath)
        full_path = os.path.join(folder, backup_filename)
        shutil.copy2(full_path, self.filepath)

    def migrate_data(self, data: list[dict]) -> list[dict]:
        for item in data:
            if "is_favorite" not in item:
                item["is_favorite"] = False
            if "tags" in item and isinstance(item["tags"], str):
                item["tags"] = [t.strip() for t in item["tags"].split(",")]
        return data
