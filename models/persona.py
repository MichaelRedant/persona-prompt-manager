from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Persona:
    id: str
    name: str
    category: str
    description: str
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data):
        return Persona(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            category=data.get("category", ""),
            description=data.get("description", ""),
            tags=data.get("tags", [])
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "tags": self.tags
        }
