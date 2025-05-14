from PySide6.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QListWidgetItem, QPushButton, QMessageBox,
    QApplication, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from models.persona import Persona
from models.prompt import Prompt
from ui.prompt_form import PromptForm
from ui.persona_form import PersonaForm
import json


def wrap_in_card(widget: QWidget, title: str = None) -> QFrame:
    frame = QFrame()
    layout = QVBoxLayout(frame)

    if title:
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
        """)
        layout.addWidget(title_label)

    layout.addWidget(widget)

    frame.setStyleSheet("""
        QFrame {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            padding: 12px;
        }
    """)
    return frame


class ClickCatcherFrame(QFrame):
    def __init__(self, parent=None, on_click=None):
        super().__init__(parent)
        self.on_click = on_click
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")
        self.setFrameShape(QFrame.NoFrame)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click()
        super().mousePressEvent(event)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prompt Library Manager")

        menu = self.menuBar()

# Bestand menu
        file_menu = menu.addMenu("Bestand")
        exit_action = file_menu.addAction("Afsluiten")
        exit_action.triggered.connect(self.close)

# Bewerken menu
        edit_menu = menu.addMenu("Bewerken")
        edit_menu.addAction("Nieuwe Persona").triggered.connect(self.add_persona)
        edit_menu.addAction("Nieuwe Prompt").triggered.connect(self.add_prompt)

# Help menu
        help_menu = menu.addMenu("Help")
        help_menu.addAction("Over").triggered.connect(self.show_about)


        self.setGeometry(100, 100, 1000, 600)

        title_label = QLabel("🧠 Prompt Library Manager")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 800;
            color: #1e3a8a;
            padding: 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            background-color: #eef2ff;
        """)


        # GUI-elementen
        self.persona_list = QListWidget()
        self.prompt_list = QListWidget()
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.prompt_details_box = QTextEdit()
        self.prompt_details_box.setReadOnly(True)

        self.add_prompt_button = QPushButton("➕ Nieuwe Prompt")
        self.edit_prompt_button = QPushButton("✏️ Bewerken Prompt")
        self.delete_prompt_button = QPushButton("❌ Verwijderen Prompt")
        self.copy_prompt_button = QPushButton("📋 Kopiëren naar klembord")

        self.add_persona_button = QPushButton("➕ Nieuwe Persona")
        self.edit_persona_button = QPushButton("✏️ Bewerken Persona")
        self.delete_persona_button = QPushButton("❌ Verwijderen Persona")

        self.edit_prompt_button.hide()
        self.delete_prompt_button.hide()
        self.copy_prompt_button.hide()
        self.edit_persona_button.hide()
        self.delete_persona_button.hide()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Zoek op persona, prompt of tag...")

        self.persona_list.setFocusPolicy(Qt.StrongFocus)
        self.prompt_list.setFocusPolicy(Qt.StrongFocus)



        # Hoofdlayout
        layout = QVBoxLayout()
        layout.addWidget(title_label)

        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Lijsten (Persona + Prompt)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(24)
        layout.addWidget(wrap_in_card(self.search_input, "🔍 Zoek"))
        top_layout.addWidget(wrap_in_card(self.persona_list, "📚 Persona's"))
        top_layout.addWidget(wrap_in_card(self.prompt_list, "💡 Prompts"))
        layout.addLayout(top_layout)

        # Inhoudelijke blokken
        layout.addWidget(wrap_in_card(self.details_box, "🧠 Beschrijving"))
        layout.addWidget(wrap_in_card(self.prompt_details_box, "✏️ Promptdetails"))

        # Personaknoppen
        persona_btns = QHBoxLayout()
        persona_btns.setSpacing(10)
        persona_btns.addWidget(self.add_persona_button)
        persona_btns.addWidget(self.edit_persona_button)
        persona_btns.addWidget(self.delete_persona_button)
        layout.addLayout(persona_btns)

        # Promptknoppen
        prompt_btns = QHBoxLayout()
        prompt_btns.setSpacing(10)
        prompt_btns.addWidget(self.add_prompt_button)
        prompt_btns.addWidget(self.edit_prompt_button)
        prompt_btns.addWidget(self.delete_prompt_button)
        prompt_btns.addWidget(self.copy_prompt_button)
        layout.addLayout(prompt_btns)

        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Data
        self.load_prompts()
        self.load_personas()

        # Events
        self.persona_list.currentRowChanged.connect(self.display_persona_details)
        self.prompt_list.itemSelectionChanged.connect(
            lambda: self.display_prompt_details(self.prompt_list.currentRow())
        )
        self.search_input.textChanged.connect(self.perform_search)
        self.add_prompt_button.clicked.connect(self.add_prompt)
        self.edit_prompt_button.clicked.connect(self.edit_prompt)
        self.delete_prompt_button.clicked.connect(self.delete_prompt)
        self.copy_prompt_button.clicked.connect(self.copy_prompt)
        self.add_persona_button.clicked.connect(self.add_persona)
        self.edit_persona_button.clicked.connect(self.edit_persona)
        self.delete_persona_button.clicked.connect(self.delete_persona)
        self.persona_list.itemSelectionChanged.connect(self.check_selection_state)
        self.prompt_list.itemSelectionChanged.connect(self.check_selection_state)

        # Voeg overlay toe die clicks opvangt
        self.click_catcher = ClickCatcherFrame(self, self.clear_selections)
        self.click_catcher.setGeometry(self.rect())
        self.click_catcher.raise_()  # Zorg dat hij boven alles zit
        self.click_catcher.lower()   # Behalve boven alles wat klikbaar is



    def load_personas(self):
        with open("storage/db.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.personas = [Persona.from_dict(item) for item in data]
        for persona in self.personas:
            self.persona_list.addItem(persona.name)

    def load_prompts(self):
        try:
            with open("storage/prompts.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.prompts = [Prompt.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Fout bij laden prompts.json: {e}")
            self.prompts = []

    def display_persona_details(self, index):
        if index >= 0:
            persona = self.filtered_personas[index] if hasattr(self, 'filtered_personas') else self.personas[index]
            self.details_box.setPlainText(
            f"🔹 Naam: {persona.name}\n"
                f"🔹 Categorie: {persona.category}\n"
                f"🔹 Tags: {', '.join(persona.tags)}\n\n"
                f"{persona.description}"
            )
            self.edit_persona_button.show()
            self.delete_persona_button.show()

            self.prompt_list.clear()
            related_prompts = [p for p in self.prompts if p.persona_id == persona.id]
            for prompt in related_prompts:
                item = QListWidgetItem(prompt.title)
                item.setData(Qt.UserRole, prompt.id)
                self.prompt_list.addItem(item)

            if self.prompt_list.count() > 0:
                self.prompt_list.setCurrentRow(0)
        else:
            self.details_box.clear()
            self.prompt_list.clear()
            self.prompt_details_box.clear()
            self.edit_persona_button.hide()
            self.delete_persona_button.hide()
            self.edit_prompt_button.hide()
            self.delete_prompt_button.hide()
            self.copy_prompt_button.hide()

        # ❗ Toon opnieuw enkel de + knoppen
            self.add_persona_button.show()
            self.add_prompt_button.show()


    def display_prompt_details(self, index):
        if index >= 0:
            item = self.prompt_list.item(index)
            prompt_id = item.data(Qt.UserRole)
            prompt = next((p for p in self.prompts if p.id == prompt_id), None)

            if prompt:
                self.edit_prompt_button.show()
                self.delete_prompt_button.show()
                self.copy_prompt_button.show()

            # Zoek bijbehorende persona
                persona = next((p for p in self.personas if p.id == prompt.persona_id), None)
                if persona:
                    self.details_box.setPlainText(
                        f"🔹 Naam: {persona.name}\n"
                        f"🔹 Categorie: {persona.category}\n"
                        f"🔹 Tags: {', '.join(persona.tags)}\n\n"
                        f"{persona.description}"
                    )

                self.prompt_details_box.setPlainText(
                    f"📝 Titel: {prompt.title}\n"
                    f"🏷️ Tags: {', '.join(prompt.tags)}\n"
                    f"📅 Laatst gebruikt: {prompt.last_used}\n\n"
                    f"{prompt.content}"
                )
        else:
            self.edit_prompt_button.hide()
            self.delete_prompt_button.hide()
            self.copy_prompt_button.hide()
            self.prompt_details_box.clear()

            if self.persona_list.currentRow() == -1:
                self.details_box.clear()
                self.add_persona_button.show()
                self.add_prompt_button.show()

    def refresh_persona_list(self):
        self.persona_list.clear()
        for persona in self.personas:
            self.persona_list.addItem(persona.name)

    def add_prompt(self):
        persona_index = self.persona_list.currentRow()
        if persona_index < 0:
            return
        persona = self.personas[persona_index]
        dialog = PromptForm(persona.id, self)
        if dialog.exec():
            new_prompt = dialog.get_prompt()
            self.prompts.append(new_prompt)
            with open("storage/prompts.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)
            self.display_persona_details(persona_index)

    def edit_prompt(self):
        persona_index = self.persona_list.currentRow()
        prompt_index = self.prompt_list.currentRow()
        if persona_index < 0 or prompt_index < 0:
            return
        item = self.prompt_list.item(prompt_index)
        prompt_id = item.data(Qt.UserRole)
        prompt = next((p for p in self.prompts if p.id == prompt_id), None)
        if not prompt:
            return
        dialog = PromptForm(prompt.persona_id, self, prompt)
        if dialog.exec():
            updated = dialog.get_prompt()
            for i, p in enumerate(self.prompts):
                if p.id == updated.id:
                    self.prompts[i] = updated
                    break
            with open("storage/prompts.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)
            self.display_persona_details(persona_index)
            self.prompt_list.setCurrentRow(prompt_index)

    def delete_prompt(self):
        persona_index = self.persona_list.currentRow()
        prompt_index = self.prompt_list.currentRow()
        if persona_index < 0 or prompt_index < 0:
            return
        item = self.prompt_list.item(prompt_index)
        prompt_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Bevestigen",
            "Ben je zeker dat je deze prompt wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.prompts = [p for p in self.prompts if p.id != prompt_id]
            with open("storage/prompts.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)
            self.display_persona_details(persona_index)
            self.prompt_details_box.clear()

    def copy_prompt(self):
        prompt_index = self.prompt_list.currentRow()
        if prompt_index < 0:
            return
        item = self.prompt_list.item(prompt_index)
        prompt_id = item.data(Qt.UserRole)
        prompt = next((p for p in self.prompts if p.id == prompt_id), None)
        if prompt:
            full_text = f"{prompt.title}\n\n{prompt.content}"
            QApplication.clipboard().setText(full_text)
            msg = QMessageBox(self)
            msg.setWindowTitle("Gekopieerd")
            msg.setText("✅ Prompt gekopieerd naar klembord.")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def add_persona(self):
        dialog = PersonaForm(self)
        if dialog.exec():
            new_persona = dialog.get_persona()
            self.personas.append(new_persona)
            with open("storage/db.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)
            self.refresh_persona_list()

    def edit_persona(self):
        index = self.persona_list.currentRow()
        if index < 0:
            return
        persona = self.personas[index]
        dialog = PersonaForm(self, persona)
        if dialog.exec():
            updated = dialog.get_persona()
            self.personas[index] = updated
            with open("storage/db.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)
            self.refresh_persona_list()
            self.persona_list.setCurrentRow(index)

    def delete_persona(self):
        index = self.persona_list.currentRow()
        if index < 0:
            return
        persona = self.personas[index]
        reply = QMessageBox.question(
            self, "Bevestigen",
            f"Ben je zeker dat je '{persona.name}' wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.personas[index]
            with open("storage/db.json", "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)
            self.refresh_persona_list()
            self.details_box.clear()
            self.prompt_list.clear()
            self.prompt_details_box.clear()

    def perform_search(self, query: str):
        query = query.lower().strip()

        self.persona_list.clear()
        self.prompt_list.clear()
        self.details_box.clear()
        self.prompt_details_box.clear()

        self.filtered_personas = []
        self.filtered_prompts = []

        if not query:
            self.filtered_personas = self.personas.copy()
            for persona in self.filtered_personas:
                self.persona_list.addItem(persona.name)
            self.persona_list.setCurrentRow(0)
            return

    # Zoek in persona's
        for persona in self.personas:
            persona_text = " ".join([
                persona.name,
                persona.category,
                " ".join(persona.tags)
            ]).lower()

            if query in persona_text:
                self.persona_list.addItem(persona.name)
                self.filtered_personas.append(persona)

    # Zoek in prompts
        for prompt in self.prompts:
            prompt_text = " ".join([
                prompt.title,
                prompt.content,
                " ".join(prompt.tags)
            ]).lower()

            if query in prompt_text:
                self.filtered_prompts.append(prompt)
                item = QListWidgetItem(prompt.title)
                item.setData(Qt.UserRole, prompt.id)
                self.prompt_list.addItem(item)

    # Toon eerste prompt detail als er match is
        if self.prompt_list.count() > 0:
            self.prompt_list.setCurrentRow(0)

    def show_about(self):
        QMessageBox.information(
            self,
            "Over Prompt Manager",
            "🧠 Gemaakt door Michaël Redant\nVersie 1.0\nPySide6 Applicatie"
        )

    def check_selection_state(self):
        if self.persona_list.currentRow() == -1 and self.prompt_list.currentRow() == -1:
            self.details_box.clear()
            self.prompt_details_box.clear()

            self.edit_persona_button.hide()
            self.delete_persona_button.hide()
            self.edit_prompt_button.hide()
            self.delete_prompt_button.hide()
            self.copy_prompt_button.hide()

            self.add_persona_button.show()
            self.add_prompt_button.show()

    def clear_selections(self):
        self.persona_list.clearSelection()
        self.prompt_list.clearSelection()
        self.details_box.clear()
        self.prompt_details_box.clear()

        self.edit_persona_button.hide()
        self.delete_persona_button.hide()
        self.edit_prompt_button.hide()
        self.delete_prompt_button.hide()
        self.copy_prompt_button.hide()

        self.add_persona_button.show()
        self.add_prompt_button.show()


