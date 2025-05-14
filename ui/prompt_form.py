from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout
)
from models.prompt import Prompt
from datetime import datetime
import uuid

class PromptForm(QDialog):
    def __init__(self, persona_id, parent=None, prompt: Prompt = None):
        super().__init__(parent)
        self.setWindowTitle("Prompt Bewerken" if prompt else "Nieuwe Prompt")
        self.setMinimumWidth(400)
        self.persona_id = persona_id
        self.existing_prompt = prompt

        layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.content_input = QTextEdit()
        self.tags_input = QLineEdit()

        layout.addWidget(QLabel("Titel"))
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Prompttekst"))
        layout.addWidget(self.content_input)

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

        if prompt:
            self.title_input.setText(prompt.title)
            self.content_input.setPlainText(prompt.content)
            self.tags_input.setText(", ".join(prompt.tags))

    def get_prompt(self):
        return Prompt(
            id=self.existing_prompt.id if self.existing_prompt else str(uuid.uuid4()),
            persona_id=self.persona_id,
            title=self.title_input.text(),
            content=self.content_input.toPlainText(),
            tags=[tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()],
            last_used=datetime.now().strftime("%Y-%m-%d")
        )
