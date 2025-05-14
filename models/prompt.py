from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Prompt:
    id: str
    persona_id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    last_used: str = ""

    @staticmethod
    def from_dict(data):
        return Prompt(
            id=data.get("id", str(uuid.uuid4())),
            persona_id=data["persona_id"],
            title=data["title"],
            content=data["content"],
            tags=data.get("tags", []),
            last_used=data.get("last_used", "")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "persona_id": self.persona_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "last_used": self.last_used
        }
