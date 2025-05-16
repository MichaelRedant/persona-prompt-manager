from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QWidget, QComboBox
)
from PySide6.QtCore import Qt
from models.prompt import Prompt
import uuid
import datetime

class PromptForm(QDialog):
    def __init__(self, parent=None, prompt=None, personas=None, preselected_persona=None):
        super().__init__(parent)
        self.setWindowTitle("💬 Prompt toevoegen of bewerken")
        self.setMinimumSize(600, 650)

        self.prompt = prompt
        self.personas = personas or []
        self.preselected_persona = preselected_persona

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)

        # 📇 Persona dropdown
        self.persona_dropdown = QComboBox()
        self.persona_id_map = {}  # index => persona.id
        form_layout.addWidget(QLabel("📇 Koppel aan Persona *"))
        form_layout.addWidget(self.persona_dropdown)
        self.persona_dropdown.setStyleSheet("""
    QComboBox {
        padding: 8px;
        font-size: 14px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        background-color: white;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left-width: 1px;
        border-left-color: #d1d5db;
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }
    QComboBox QAbstractItemView {
        font-size: 14px;
        selection-background-color: #e0e7ff;
        selection-color: #1e3a8a;
        padding: 6px;
    }
""")

        for persona in self.personas:
            self.persona_dropdown.addItem(persona.name, userData=persona.id)


        # 👉 Automatisch de vooraf geselecteerde persona kiezen
        if self.preselected_persona:
            index = self.persona_dropdown.findData(self.preselected_persona.id)
            if index != -1:
                self.persona_dropdown.setCurrentIndex(index)


        # ⚡ Titel
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Bijv. 'Lead intro e-mail', 'Samenvatting blog'...")
        form_layout.addWidget(QLabel("⚡ Interne naam van deze prompt *"))
        form_layout.addWidget(self.title_input)

        # 🏷️ Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Bijv. SEO, mail, educatie")
        form_layout.addWidget(QLabel("🏷️ Tags (optioneel)"))
        form_layout.addWidget(self.tags_input)

        # 📝 Promptinhoud
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Schrijf hier de volledige prompt voor GPT...")
        form_layout.addWidget(QLabel("📝 Promptinhoud *"))
        form_layout.addWidget(self.content_input)

        # 💾 Knoppen
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

        # ✏️ Prompt bewerken: bestaande data invullen
        if self.prompt:
            self.title_input.setText(self.prompt.title)
            self.tags_input.setText(", ".join(self.prompt.tags))
            self.content_input.setPlainText(self.prompt.content)

            for i, persona in enumerate(self.personas):
                if persona.id == self.prompt.persona_id:
                    self.persona_dropdown.setCurrentIndex(i)
                    break

        # Connect knoppen
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        index = self.persona_dropdown.currentIndex()
        persona_id = self.persona_id_map.get(index)

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
