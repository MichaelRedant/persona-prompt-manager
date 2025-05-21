# ui/persona_form.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QComboBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from models.persona import Persona
import uuid

class PersonaForm(QDialog):
    def __init__(self, parent=None, persona=None, template_mode=False):
        super().__init__(parent)
        self.setWindowTitle("➕ Nieuwe Persona")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel, QLineEdit, QTextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)

        self.persona = persona
        self.template_mode = template_mode

        layout = QVBoxLayout(self)

        title = QLabel("🧠 Voeg een nieuwe persona toe")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e3a8a; margin-bottom: 24px;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Naam van de persona")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Categorie of rol")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Beschrijf deze persona...")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (komma-gescheiden, bv: creatief, ux, seo)")

        layout.addWidget(QLabel("🔤 Naam"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("🏷️ Categorie"))
        layout.addWidget(self.category_input)
        layout.addWidget(QLabel("📝 Beschrijving"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("🔖 Tags"))
        layout.addWidget(self.tags_input)

        btns = QHBoxLayout()
        save_btn = QPushButton("💾 Opslaan")
        cancel_btn = QPushButton("❌ Annuleren")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)

        layout.addSpacing(12)
        layout.addLayout(btns)

        # Indien bewerken: velden vooraf invullen
        if persona:
            self.name_input.setText(persona.name)
            self.category_input.setText(persona.category)
            self.description_input.setPlainText(persona.description)
            self.tags_input.setText(", ".join(persona.tags))


    def get_persona(self):
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        description = self.description_input.toPlainText().strip()
        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
    
        if not name or not category or not description:
            return None
    
        persona_id = self.persona.id if self.persona else str(uuid.uuid4())
    
        return Persona(
            id=persona_id,
            name=name,
            category=category,
            description=description,
            tags=tags
        )

