from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from models.persona import Persona
import uuid

class PersonaForm(QDialog):
    def __init__(self, parent=None, persona=None):
        super().__init__(parent)
        self.setWindowTitle("🧠 Persona toevoegen of bewerken")
        self.setMinimumSize(600, 700)

        self.persona = persona

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)

        # Naam (verplicht)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Bijv. Senior Python Developer")
        form_layout.addWidget(QLabel("Naam *"))
        form_layout.addWidget(self.name_input)

        # Categorie
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Bijv. Development, Marketing...")
        form_layout.addWidget(QLabel("Categorie"))
        form_layout.addWidget(self.category_input)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Bijv. python, api, backend")
        form_layout.addWidget(QLabel("Tags (gescheiden door komma's)"))
        form_layout.addWidget(self.tags_input)

        # Vrije tekstveld (alle inhoud zelf te structureren)
        self.full_text_input = QTextEdit()
        self.full_text_input.setPlaceholderText(
            "Voer hier je volledige persona-inhoud in (beschrijving, workflows, toon, structuur...)."
        )
        form_layout.addWidget(QLabel("Volledige Persona Inhoud"))
        form_layout.addWidget(self.full_text_input)

        # Buttons
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

        # Data invullen indien edit
        if self.persona:
            self.name_input.setText(self.persona.name)
            self.category_input.setText(self.persona.category)
            self.tags_input.setText(", ".join(self.persona.tags))
            self.full_text_input.setPlainText(self.persona.description)

        # Connecties
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validatiefout", "Naam is verplicht.")
            return

        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        description = self.full_text_input.toPlainText()

        if self.persona:
            self.persona.name = name
            self.persona.category = self.category_input.text().strip()
            self.persona.tags = tags
            self.persona.description = description
        else:
            self.persona = Persona(
                id=str(uuid.uuid4()),
                name=name,
                category=self.category_input.text().strip(),
                tags=tags,
                description=description
            )

        super().accept()

    def get_persona(self):
        return self.persona
