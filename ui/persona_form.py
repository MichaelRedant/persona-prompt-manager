from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QHBoxLayout
)
from models.persona import Persona
import uuid

class PersonaForm(QDialog):
    def __init__(self, parent=None, persona: Persona = None):
        super().__init__(parent)
        self.setWindowTitle("Bewerk Persona" if persona else "Nieuwe Persona")
        self.setMinimumWidth(400)
        self.existing_persona = persona

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.description_input = QTextEdit()
        self.tags_input = QLineEdit()

        layout.addWidget(QLabel("Naam"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Categorie"))
        layout.addWidget(self.category_input)

        layout.addWidget(QLabel("Beschrijving"))
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("Tags (komma-gescheiden)"))
        layout.addWidget(self.tags_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Opslaan")
        self.cancel_btn = QPushButton("Annuleren")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        if persona:
            self.name_input.setText(persona.name)
            self.category_input.setText(persona.category)
            self.description_input.setPlainText(persona.description)
            self.tags_input.setText(", ".join(persona.tags))

    def get_persona(self):
        return Persona(
            id=self.existing_persona.id if self.existing_persona else str(uuid.uuid4()),
            name=self.name_input.text(),
            category=self.category_input.text(),
            description=self.description_input.toPlainText(),
            tags=[tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]
        )
