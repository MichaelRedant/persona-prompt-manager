from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QWidget, QComboBox
)
from PySide6.QtCore import Qt
from models.prompt import Prompt
from models.persona import Persona
import uuid
import datetime

class PromptForm(QDialog):
    def __init__(self, parent=None, prompt=None, personas=None, preselected_persona=None):
        super().__init__(parent)
        self.setWindowTitle("💬 Prompt toevoegen of bewerken")
        self.setMinimumSize(600, 650)

        self.prompt = prompt
        self.personas = personas or []
        self.persona_id = None

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)

        # Persona dropdown
        self.persona_select = QComboBox()
        self.persona_map = {}
        form_layout.addWidget(QLabel("Persona *"))
        form_layout.addWidget(self.persona_select)

        for persona in self.personas:
            self.persona_select.addItem(persona.name)
            self.persona_map[persona.name] = persona.id

        if preselected_persona:
            index = self.persona_select.findText(preselected_persona.name)
            if index >= 0:
                self.persona_select.setCurrentIndex(index)

        # Titel
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Bijv. Genereer code voor...")
        form_layout.addWidget(QLabel("Titel *"))
        form_layout.addWidget(self.title_input)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Bijv. debug, api, optimalisatie")
        form_layout.addWidget(QLabel("Tags"))
        form_layout.addWidget(self.tags_input)

        # Prompt inhoud
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Voer hier je volledige GPT-prompt in...")
        form_layout.addWidget(QLabel("Promptinhoud *"))
        form_layout.addWidget(self.content_input)

        # Knoppen
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 Opslaan")
        self.cancel_button = QPushButton("Annuleren")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        form_layout.addLayout(button_layout)

        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Bestaande data invullen
        if self.prompt:
            self.title_input.setText(self.prompt.title)
            self.tags_input.setText(", ".join(self.prompt.tags))
            self.content_input.setPlainText(self.prompt.content)

            # Selecteer juiste persona
            if self.prompt.persona_id:
                for name, pid in self.persona_map.items():
                    if pid == self.prompt.persona_id:
                        idx = self.persona_select.findText(name)
                        if idx >= 0:
                            self.persona_select.setCurrentIndex(idx)
                        break

        # Connect
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        persona_name = self.persona_select.currentText()
        persona_id = self.persona_map.get(persona_name)

        if not title or not content:
            QMessageBox.warning(self, "Validatiefout", "Titel en inhoud zijn verplicht.")
            return

        if not persona_id:
            QMessageBox.warning(self, "Validatiefout", "Je moet een persona kiezen.")
            return

        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        last_used = datetime.datetime.now().strftime("%Y-%m-%d")

        if self.prompt:
            self.prompt.title = title
            self.prompt.content = content
            self.prompt.tags = tags
            self.prompt.last_used = last_used
            self.prompt.persona_id = persona_id
        else:
            self.prompt = Prompt(
                id=str(uuid.uuid4()),
                persona_id=persona_id,
                title=title,
                content=content,
                tags=tags,
                last_used=last_used
            )

        super().accept()

    def get_prompt(self):
        return self.prompt
