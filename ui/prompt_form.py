# ui/prompt_form.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from models.prompt import Prompt
import uuid


class PromptForm(QDialog):
    def __init__(self, parent=None, prompt=None, personas=None, preselected_persona=None):
        super().__init__(parent)
        print("🚨 PromptForm geopend!")

        self.setWindowTitle("📝 Prompt toevoegen of bewerken")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel, QLineEdit, QTextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
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

        self.prompt = prompt
        self.personas = personas or []

        layout = QVBoxLayout(self)

        title = QLabel("💬 Vul de promptgegevens in")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e3a8a; margin-bottom: 24px;")
        layout.addWidget(title)

        self.persona_combo = QComboBox()
        for persona in self.personas:
            self.persona_combo.addItem(persona.name, userData=persona)

        if preselected_persona:
            for i in range(self.persona_combo.count()):
                persona = self.persona_combo.itemData(i)
                if persona.id == preselected_persona.id:
                    self.persona_combo.setCurrentIndex(i)
                    break

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Interne naam van deze prompt")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (komma-gescheiden, optioneel)")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Vul hier je prompttekst in...")

        layout.addWidget(QLabel("🔗 Koppel aan Persona *"))
        layout.addWidget(self.persona_combo)
        layout.addWidget(QLabel("⚡ Interne naam van deze prompt *"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("🏷️ Tags (optioneel)"))
        layout.addWidget(self.tags_input)
        layout.addWidget(QLabel("🧠 Promptinhoud *"))
        layout.addWidget(self.content_input)

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

        # Vooraf ingevulde waarden bij bewerken
        if self.prompt:
            self.title_input.setText(self.prompt.title)
            self.tags_input.setText(", ".join(self.prompt.tags))
            self.content_input.setPlainText(self.prompt.content)
            if self.prompt.persona_id:
                for i in range(self.persona_combo.count()):
                    persona = self.persona_combo.itemData(i)
                    if persona.id == self.prompt.persona_id:
                        self.persona_combo.setCurrentIndex(i)
                        break

    def get_prompt(self):
        persona_index = self.persona_combo.currentIndex()
        selected_persona = self.persona_combo.itemData(persona_index)
    
        title = self.title_input.text().strip()
        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        content = self.content_input.toPlainText().strip()
    
        if not selected_persona:
            QMessageBox.warning(self, "Validatiefout", "Je moet een persona kiezen.")
            return None
        if not title:
            QMessageBox.warning(self, "Validatiefout", "De prompt heeft een titel nodig.")
            return None
        if not content:
            QMessageBox.warning(self, "Validatiefout", "De promptinhoud mag niet leeg zijn.")
            return None
    
        prompt_id = self.prompt.id if self.prompt else str(uuid.uuid4())
    
        return Prompt(
            id=prompt_id,
            title=title,
            content=content,
            tags=tags,
            persona_id=selected_persona.id
        )

