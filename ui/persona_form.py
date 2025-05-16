from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QMessageBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from models.persona import Persona
import uuid

class PersonaForm(QDialog):
    def __init__(self, parent=None, persona=None, template_mode=False):
        super().__init__(parent)
        self.setWindowTitle("🧠 Persona aanmaken" if persona is None else "✏️ Persona bewerken")
        self.setMinimumSize(800, 700)
        self.persona = persona
        self.template_mode = template_mode
        self.persona = persona

        self.sections = [
            "Algemene Beschrijving",
            "Belangrijkste Werkzaamheden & Workflows",
            "Sectorgerichte Toepassingen",
            "Jargon & Technieken",
            "Gedragskenmerken & Profiel",
            "Doelen & Succescriteria",
            "Interactie & Samenwerking",
            "Tools & Software",
            "Typische Uitdagingen & Oplossingen",
            "Hoe deze GPT zou reageren",
            "Structuur en Datavisualisatie",
            "Vermijden van Onduidelijkheid",
            "Follow-up Vragen",
            "Samenvatting van de GPT-Stijl"
        ]

        # Scrollbare layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QVBoxLayout(scroll_content)

        # Basisvelden
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.form_layout.addWidget(QLabel("Naam *"))
        self.form_layout.addWidget(self.name_input)
        self.form_layout.addWidget(QLabel("Categorie"))
        self.form_layout.addWidget(self.category_input)
        self.form_layout.addWidget(QLabel("Tags (gescheiden door komma's)"))
        self.form_layout.addWidget(self.tags_input)

        self.section_inputs = {}

        if self.persona is None and self.template_mode:
            # 14 secties tonen
            for section in self.sections:
                label = QLabel(section)
                input_field = QTextEdit()
                input_field.setPlaceholderText(f"Voer hier {section.lower()} in...")
                self.form_layout.addWidget(label)
                self.form_layout.addWidget(input_field)
                self.section_inputs[section] = input_field
        else:
            # Vrije beschrijving (zowel blanco als bewerken)
            self.description_input = QTextEdit()
            self.form_layout.addWidget(QLabel("Beschrijving"))
            self.form_layout.addWidget(self.description_input)

        # Knoppen
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 Opslaan")
        self.cancel_button = QPushButton("Annuleren")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.form_layout.addLayout(button_layout)

        # Afsluiten
        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Indien bewerken, velden invullen
        if self.persona:
            self.name_input.setText(self.persona.name)
            self.category_input.setText(self.persona.category)
            self.tags_input.setText(", ".join(self.persona.tags))
            self.description_input.setPlainText(self.persona.description)

        # Events
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validatie", "Naam is verplicht.")
            return

        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]

        if self.persona:
            # ✏️ Bijwerken
            self.persona.name = name
            self.persona.category = self.category_input.text().strip()
            self.persona.tags = tags
            self.persona.description = self.description_input.toPlainText()
        else:
            # ➕ Nieuw: combineer secties
            sections_text = []
            for title in self.sections:
                content = self.section_inputs[title].toPlainText().strip()
                if content:
                    sections_text.append(f"### {title}\n\n{content}")
            full_description = "\n\n".join(sections_text)

            self.persona = Persona(
                id=str(uuid.uuid4()),
                name=name,
                category=self.category_input.text().strip(),
                tags=tags,
                description=full_description
            )

        super().accept()

    def get_persona(self):
        return self.persona
