# services/persona_store.py

import os
import json
from models.persona import Persona


class PersonaStore:
    def __init__(self, filepath: str = None):
        if filepath is None:
            # Pak absolute path vanuit bestandslocatie
            base_dir = os.path.dirname(os.path.abspath(__file__))  # = /services
            filepath = os.path.join(base_dir, "..", "storage", "db.json")

        self.filepath = os.path.abspath(filepath)

    def load(self) -> list[Persona]:
        print("🧭 CWD:", os.getcwd())
        print("📁 Verwacht pad:", self.filepath)
        print("📂 Bestaat bestand:", os.path.exists(self.filepath))

        if not os.path.exists(self.filepath):
            return []


        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Persona.from_dict(entry) for entry in data]
        except Exception as e:
            raise RuntimeError(f"Fout bij laden van persona’s: {e}")

    def save(self, personas: list[Persona]) -> None:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in personas], f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Fout bij opslaan van persona’s: {e}")
