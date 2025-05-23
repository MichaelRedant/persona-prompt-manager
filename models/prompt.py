# models/prompt.py

from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Prompt:
    id: str
    title: str
    content: str
    persona_id: str
    tags: List[str] = field(default_factory=list)
    last_used: str = ""
    is_favorite: bool = False  # ← HIER TOEGEVOEGD

    @staticmethod
    def from_dict(data):
        return Prompt(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            content=data["content"],
            persona_id=data["persona_id"],
            tags=data.get("tags", []),
            last_used=data.get("last_used", ""),
            is_favorite=data.get("is_favorite", False)  # ← HIER TOEGEVOEGD
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "persona_id": self.persona_id,
            "tags": self.tags,
            "last_used": self.last_used,
            "is_favorite": self.is_favorite  # ← HIER TOEGEVOEGD
        }
