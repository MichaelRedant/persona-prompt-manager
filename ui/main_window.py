from PySide6.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QListWidgetItem, QPushButton, QMessageBox,
    QApplication, QFrame, QLineEdit, QScrollArea, QFileDialog, QGraphicsDropShadowEffect, QSizePolicy, QSystemTrayIcon, QMenu
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from models.persona import Persona
from models.prompt import Prompt
from ui.prompt_form import PromptForm
from ui.persona_choice_dialog import PersonaChoiceDialog
from ui.persona_form import PersonaForm
from ui.tag_filter_panel import TagFilterPanel

import json
import os
import webbrowser
import urllib.parse

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QIcon



icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"))



class ClickCatcherFrame(QFrame):
    def __init__(self, parent=None, on_click=None):
        super().__init__(parent)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
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
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Persona Vault")
        self.setGeometry(100, 100, 1100, 800)
        self.is_dark_mode = False

        # Systeemtray
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icon.ico"), self)
        self.tray_icon.setToolTip("Persona Vault")
        tray_menu = QMenu()
        tray_menu.addAction("Sluiten", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("Bestand")
        file_menu.addAction("Exporteer persona's").triggered.connect(self.export_personas)
        file_menu.addAction("Exporteer prompts").triggered.connect(self.export_prompts)
        file_menu.addAction("Afsluiten").triggered.connect(self.close)
        edit_menu = menu.addMenu("Bewerken")
        edit_menu.addAction("Nieuwe Persona").triggered.connect(self.add_persona)
        edit_menu.addAction("Nieuwe Prompt").triggered.connect(self.add_prompt)
        help_menu = menu.addMenu("Help")
        help_menu.addAction("Over").triggered.connect(self.show_about)

        # Titel
        title_label = QLabel("🧠 Persona Vault")
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

        # Zoekfunctie
        self.search_toggle_button = QPushButton("🔍")
        self.search_toggle_button.setFixedWidth(120)
        self.search_toggle_button.setStyleSheet("""
        QPushButton {
            background-color: #4f46e5;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #4338ca;
        }
        """)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Typ om te zoeken...")
        self.search_input.hide()
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("""
        QLineEdit {
            background-color: white;
            padding: 10px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #4f46e5;
            outline: none;
        }
    """)
        self.search_toggle_button.clicked.connect(self.toggle_search_input)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        search_row.addWidget(self.search_toggle_button)
        search_row.addWidget(self.search_input)
        
        # Hoofdlayout
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.addWidget(title_label)
        layout.addLayout(search_row)

        # Persona-elementen
        self.persona_list = QListWidget()
        self.persona_list.setMinimumHeight(200)
        self.no_personas_label = QLabel("Geen persona's gevonden.")
        self.no_personas_label.setAlignment(Qt.AlignCenter)
        self.no_personas_label.hide()

        self.persona_title_label = QLabel("📚 Persona's")
        self.persona_title_label.setStyleSheet("font-size: 14px; font-weight: 600; margin-bottom: 4px;")

        persona_inner_layout = QVBoxLayout()
        persona_inner_layout.addWidget(self.persona_title_label)
        persona_inner_layout.addWidget(self.no_personas_label)
        persona_inner_layout.addWidget(self.persona_list)

        persona_card = QFrame()
        persona_card.setLayout(persona_inner_layout)
        persona_card.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            padding: 12px;
        """)

        # Prompt-elementen
        self.prompt_list = QListWidget()
        self.prompt_list.setMinimumHeight(200)
        self.no_prompts_label = QLabel("Geen prompts gevonden.")
        self.no_prompts_label.setAlignment(Qt.AlignCenter)
        self.no_prompts_label.hide()

        prompt_card_widget = self.wrap_in_card(self.prompt_list, "💡 Prompts")
        prompt_wrapper = QVBoxLayout()
        prompt_wrapper.addWidget(self.no_prompts_label)
        prompt_wrapper.addWidget(prompt_card_widget)

        prompt_card_container = QFrame()
        prompt_card_container.setLayout(prompt_wrapper)

        # Tag panel
        from ui.tag_filter_panel import TagFilterPanel
        self.tag_panel = TagFilterPanel(self, self.filter_by_tag)

        # Bovenste 3-koloms layout
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        top_layout.addWidget(persona_card, 4)
        top_layout.addWidget(prompt_card_container, 3)
        top_layout.addWidget(self.tag_panel, 2)
        layout.addLayout(top_layout)

        # Promptdetails
        self.prompt_details_box = QTextEdit()
        self.prompt_details_box.setReadOnly(True)
        self.prompt_details_box.setMinimumHeight(200)

        prompt_card = self.wrap_in_card(self.prompt_details_box, "✏️ Prompttekst")

        self.copy_prompt_button = QPushButton("📋 Kopieer prompt")
        self.copy_prompt_button.clicked.connect(self.copy_prompt)
        self.copy_prompt_button.setCursor(Qt.PointingHandCursor)
        self.copy_prompt_button.setStyleSheet("""
        QPushButton {
            background-color: #4f46e5;
            color: white;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #4338ca;
        }
    """)
        self.prompt_info_label = QLabel()
        self.prompt_info_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        self.prompt_info_label.setWordWrap(True)
        self.prompt_tip_label = QLabel("💡 Tip: Start prompts met een duidelijke rol, zoals \"Je bent een expert copywriter...\")")
        self.prompt_tip_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        self.prompt_tip_label.setWordWrap(True)
        self.try_prompt_button = QPushButton("🧪 Test prompt in ChatGPT")
        self.try_prompt_button.clicked.connect(self.try_prompt_in_chatgpt)
        self.try_prompt_button.setCursor(Qt.PointingHandCursor)
        self.try_prompt_button.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
    """)

        test_button_box = QVBoxLayout()
        test_button_box.addWidget(self.copy_prompt_button)
        test_button_box.addWidget(self.prompt_info_label)
        test_button_box.addWidget(self.prompt_tip_label)
        test_button_box.addStretch()
        test_button_box.addWidget(self.try_prompt_button)

        test_card = QFrame()
        test_card.setLayout(test_button_box)
        test_card.setStyleSheet("background-color: transparent;")

        prompt_row = QHBoxLayout()
        prompt_row.setSpacing(20)
        prompt_row.addWidget(prompt_card, 5)
        prompt_row.addWidget(test_card, 3)
        layout.addLayout(prompt_row)

        # Beschrijving
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setMinimumHeight(220)
        self.details_box.setMaximumHeight(400)
        layout.addWidget(self.wrap_in_card(self.details_box, "🧠 Beschrijving"))

        # Metadata
        self.prompt_metadata_label = QLabel()
        self.prompt_metadata_label.setStyleSheet("font-size: 12px; color: #6b7280; padding-left: 12px; padding-top: 4px;")
        layout.addWidget(self.prompt_metadata_label)

        # Knoppen persona
        self.add_persona_button = QPushButton("➕ Nieuwe Persona")
        self.edit_persona_button = QPushButton("✏️ Bewerken Persona")
        self.delete_persona_button = QPushButton("❌ Verwijderen Persona")
        self.favorite_button = QPushButton("⭐ Toggle Favoriet")
        persona_btns = QHBoxLayout()
        persona_btns.addWidget(self.add_persona_button)
        persona_btns.addWidget(self.edit_persona_button)
        persona_btns.addWidget(self.delete_persona_button)
        persona_btns.addWidget(self.favorite_button)
        layout.addLayout(persona_btns)

        # Knoppen prompt
        self.add_prompt_button = QPushButton("➕ Nieuwe Prompt")
        self.edit_prompt_button = QPushButton("✏️ Bewerken Prompt")
        self.delete_prompt_button = QPushButton("❌ Verwijderen Prompt")
        prompt_btns = QHBoxLayout()
        prompt_btns.addWidget(self.add_prompt_button)
        prompt_btns.addWidget(self.edit_prompt_button)
        prompt_btns.addWidget(self.delete_prompt_button)
        layout.addLayout(prompt_btns)

        # Scrollcontainer
        container_widget = QWidget()
        container_widget.setLayout(layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 12px;
                margin: 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        self.setCentralWidget(scroll_area)

        # --- Laad data
        self.load_prompts()
        self.load_personas()

        # --- Events koppelen
        self.persona_list.currentRowChanged.connect(self.display_persona_details)
        self.prompt_list.itemSelectionChanged.connect(lambda: self.display_prompt_details(self.prompt_list.currentRow()))
        self.search_input.textChanged.connect(self.perform_search)
        self.add_prompt_button.clicked.connect(self.add_prompt)
        self.edit_prompt_button.clicked.connect(self.edit_prompt)
        self.delete_prompt_button.clicked.connect(self.delete_prompt)
        self.copy_prompt_button.clicked.connect(self.copy_prompt)
        self.add_persona_button.clicked.connect(self.add_persona)
        self.edit_persona_button.clicked.connect(self.edit_persona)
        self.delete_persona_button.clicked.connect(self.delete_persona)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.persona_list.itemSelectionChanged.connect(self.check_selection_state)
        self.prompt_list.itemSelectionChanged.connect(self.check_selection_state)

        # --- Click catcher om selectie leeg te maken
        self.click_catcher = ClickCatcherFrame(self, self.clear_selections)
        self.click_catcher.setGeometry(self.rect())
        self.click_catcher.raise_()
        self.click_catcher.lower()



    def load_personas(self):
        try:
            # Dynamisch pad naar JSON, werkt ook bij gebundelde .exe
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "storage", "db.json")

            # JSON inlezen
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Data laden in objecten
            self.personas = [Persona.from_dict(item) for item in data]

        except FileNotFoundError:
            QMessageBox.warning(self, "Bestand niet gevonden",
                                "⚠️ Het bestand 'storage/db.json' werd niet gevonden.")
            self.personas = []

        except json.JSONDecodeError:
            QMessageBox.critical(self, "JSON-fout",
                                "🚫 Fout bij het inlezen van 'db.json'. Controleer de opmaak.")
            self.personas = []

        except Exception as e:
            QMessageBox.critical(self, "Onverwachte fout",
                                f"❌ Er is een fout opgetreden bij het laden van de persona's:\n{e}")
            self.personas = []

        # UI bijwerken
        self.refresh_persona_list()
        self.update_persona_title()
        self.tag_panel.update_tags(self.personas, self.prompts)


    def load_prompts(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompts_path = os.path.join(base_dir, "storage", "prompts.json")

            if not os.path.exists(prompts_path):
                self.prompts = []
                return

            with open(prompts_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.prompts = []
                    return
                data = json.loads(content)
                self.prompts = [Prompt.from_dict(item) for item in data]

        except json.JSONDecodeError:
            QMessageBox.critical(self, "JSON-fout",
                "🚫 Fout bij het inlezen van 'prompts.json'. Controleer de opmaak.")
            self.prompts = []
            self.tag_panel.update_tags(self.personas, self.prompts)
            

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
                item.setData(Qt.UserRole, prompt.id)  # Belangrijk!
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

            self.add_persona_button.show()
            self.add_prompt_button.show()
            self.favorite_button.show()

    def display_prompt_details(self, index):
        if index >= 0:
            item = self.prompt_list.item(index)
            prompt_id = item.data(Qt.UserRole)
            prompt = next((p for p in self.prompts if p.id == prompt_id), None)

            if prompt:
                self.edit_prompt_button.show()
                self.delete_prompt_button.show()
                self.copy_prompt_button.show()
                persona = next((p for p in self.personas if p.id == prompt.persona_id), None)
                persona_name = persona.name if persona else "Ongekend"
                length = len(prompt.content)
                self.prompt_info_label.setText(
                    f"🔗 Koppeling: <b>{persona_name}</b> · 📏 Lengte: {length} tekens · 🕒 Laatst gebruikt: {prompt.last_used}"
                )

                # Dynamische tips (optioneel randomiseren)
                tips = [
                    "💡 Tip: Start prompts met een duidelijke rol, zoals “Je bent een expert copywriter...”",
                    "💡 Tip: Wees specifiek over output: 'Geef me 3 opsommingen' i.p.v. 'Schrijf iets'",
                    "💡 Tip: Gebruik context: 'Je werkt voor een startup in gezondheidszorg...'",
                ]
                import random
                self.prompt_tip_label.setText(random.choice(tips))
                self.prompt_details_box.setPlainText(prompt.content)

                persona = next((p for p in self.personas if p.id == prompt.persona_id), None)
                if persona:
                    self.details_box.setPlainText(
                        f"🔹 Naam: {persona.name}\n"
                        f"🔹 Categorie: {persona.category}\n"
                        f"🔹 Tags: {', '.join(persona.tags)}\n\n"
                        f"{persona.description}"
                    )

                self.prompt_metadata_label.setText(
                    f"<i>{prompt.title}</i> · Tags: {', '.join(prompt.tags)} · Laatst gebruikt: {prompt.last_used}"
                )
        else:
            self.edit_prompt_button.hide()
            self.delete_prompt_button.hide()
            self.copy_prompt_button.hide()
            self.prompt_details_box.clear()
            self.details_box.clear()
            self.prompt_metadata_label.clear()


    def refresh_persona_list(self):
        self.persona_list.clear()
        self.no_personas_label.setVisible(self.persona_list.count() == 0)
        self.update_persona_title()



    # Sorteer favorieten eerst, dan alfabetisch
        self.filtered_personas = sorted(
            self.personas,
            key=lambda p: (not p.is_favorite, p.name.lower())
        )

        for persona in self.filtered_personas:
            label = f"⭐ {persona.name}" if persona.is_favorite else f"☆ {persona.name}"
            item = QListWidgetItem(label)
            self.persona_list.addItem(item)
            self.no_personas_label.setVisible(len(self.filtered_personas) == 0)


    def add_prompt(self):
        selected_persona = None
        persona_index = self.persona_list.currentRow()
        if 0 <= persona_index < len(self.personas):
            selected_persona = self.personas[persona_index]

        dialog = PromptForm(
            self,
            personas=self.personas,
            preselected_persona=selected_persona
        )

        if dialog.exec():
            new_prompt = dialog.get_prompt()
            if not new_prompt:
                return

            self.prompts.append(new_prompt)

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompts_path = os.path.join(base_dir, "storage", "prompts.json")

            with open(prompts_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)

            if selected_persona:
                self.display_persona_details(persona_index)

            # Tags bijwerken
            self.tag_panel.update_tags(self.personas, self.prompts)




    def edit_prompt(self):
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Selectie vereist", "Selecteer een prompt om te bewerken.")
            return

        prompt_id = current_item.data(Qt.UserRole)
        selected_prompt = next((p for p in self.prompts if p.id == prompt_id), None)

        if not selected_prompt:
            QMessageBox.warning(self, "Ongeldig", "Kon de geselecteerde prompt niet vinden.")
            return

        # Zoek bijhorende persona
        selected_persona = next((p for p in self.personas if p.id == selected_prompt.persona_id), None)

        dialog = PromptForm(
            self,
            prompt=selected_prompt,
            personas=self.personas,
            preselected_persona=selected_persona
        )

        if dialog.exec():
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompts_path = os.path.join(base_dir, "storage", "prompts.json")

            with open(prompts_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)

            self.display_persona_details(self.persona_list.currentRow())
            self.tag_panel.update_tags(self.personas, self.prompts)



    def delete_prompt(self):
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Selectie vereist", "Selecteer een prompt om te verwijderen.")
            return

        prompt_id = current_item.data(Qt.UserRole)
        selected_prompt = next((p for p in self.prompts if p.id == prompt_id), None)

        if not selected_prompt:
            QMessageBox.warning(self, "Niet gevonden", "Geselecteerde prompt kon niet worden gevonden.")
            return

        confirm = QMessageBox.question(
            self,
            "Bevestig verwijderen",
            f"Weet je zeker dat je deze prompt wil verwijderen?\n\n{selected_prompt.title}"
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.prompts = [p for p in self.prompts if p.id != selected_prompt.id]

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompts_path = os.path.join(base_dir, "storage", "prompts.json")

            with open(prompts_path, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)


                self.display_persona_details(self.persona_list.currentRow())

        self.tag_panel.update_tags(self.personas, self.prompts)


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
        dialog = PersonaChoiceDialog(self)
        result = dialog.exec()

        if result == 1:
            persona_form = PersonaForm(self, persona=None, template_mode=False)
        elif result == 2:
            persona_form = PersonaForm(self, persona=None, template_mode=True)
        else:
            return  # geannuleerd

        if persona_form.exec():
            new_persona = persona_form.get_persona()
            self.personas.append(new_persona)
            self.save_personas()
            self.refresh_persona_list()
            self.tag_panel.update_tags(self.personas, self.prompts)





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
            self.update_persona_title()
            self.persona_list.setCurrentRow(index)
            self.tag_panel.update_tags(self.personas, self.prompts)


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
            self.update_persona_title()

            self.details_box.clear()
            self.prompt_list.clear()
            self.prompt_details_box.clear()
            self.tag_panel.update_tags(self.personas, self.prompts)


    def perform_search(self, query: str):
        query = query.lower().strip()

        self.persona_list.clear()
        self.prompt_list.clear()
        self.details_box.clear()
        self.prompt_details_box.clear()
        self.update_persona_title()

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
                self.no_personas_label.setVisible(len(self.filtered_personas) == 0)

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
                self.no_prompts_label.setVisible(self.prompt_list.count() == 0)


    # Toon eerste prompt detail als er match is
        if self.prompt_list.count() > 0:
            self.prompt_list.setCurrentRow(0)
            self.no_prompts_label.setVisible(self.prompt_list.count() == 0)
            

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
            self.favorite_button.hide()


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
        self.favorite_button.hide()

        
    def toggle_search_input(self):
        self.search_input.setVisible(not self.search_input.isVisible())
        if self.search_input.isVisible():
            self.search_input.setFocus()
        else:
            self.search_input.clear()
            self.perform_search("")

    def toggle_favorite(self):
        index = self.persona_list.currentRow()
        if index < 0:
            return

        persona = self.filtered_personas[index]
        persona.is_favorite = not persona.is_favorite

    # Opslaan
        with open("storage/db.json", "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)

        self.refresh_persona_list()
        
    def toggle_favorite_by_click(self, item: QListWidgetItem):
        index = self.persona_list.row(item)
        if index < 0 or not hasattr(self, 'filtered_personas'):
            return

        persona = self.filtered_personas[index]
        persona.is_favorite = not persona.is_favorite

    # Opslaan
        with open("storage/db.json", "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)

        self.refresh_persona_list()


    def toggle_dark_mode(self, enabled):
        self.is_dark_mode = enabled
        self.refresh_persona_list()
        self.rebuild_layout()

        if enabled:
            self.setStyleSheet("""
                * { background-color: #1e1e1e; color: #e0e0e0; }
                QLineEdit, QTextEdit, QListWidget, QMenuBar, QMenu {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)
        else:
            self.setStyleSheet("")

        self.update()


    def export_personas(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export persona's", "personas.json", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)

    def export_prompts(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export prompts", "prompts.json", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)
                
                
                
    def rebuild_layout(self):
    # Bewaar huidige selectie en zoekterm (optioneel)
        search = self.search_input.text()
        self.search_input.clear()

    # Verwijder en heropbouw layout
        self.centralWidget().deleteLater()
        self.__init__()  # Ja, dit is hier ok: herlaadt alles proper
        self.search_input.setText(search)
           
    
    def update_persona_title(self):
        count = len(self.filtered_personas) if hasattr(self, 'filtered_personas') else len(self.personas)
        self.persona_title_label.setText(f"📚 Persona's {count}")
            
    def add_blank_persona(self):
        from ui.persona_form import PersonaForm
        dialog = PersonaForm(self, persona=None, template_mode=False)
        if dialog.exec():
            new_persona = dialog.get_persona()
            self.personas.append(new_persona)
            self.save_personas()
            self.refresh_persona_list()

    def add_template_persona(self):
        from ui.persona_form import PersonaForm
        dialog = PersonaForm(self, persona=None, template_mode=True)
        if dialog.exec():
            new_persona = dialog.get_persona()
            self.personas.append(new_persona)
            self.save_personas()
            self.refresh_persona_list()

    def filter_by_tag(self, tag):
        self.persona_list.clear()
        self.prompt_list.clear()
        self.details_box.clear()
        self.prompt_details_box.clear()
    
        if not tag:
            self.filtered_personas = self.personas.copy()
        else:
            self.filtered_personas = [p for p in self.personas if tag in p.tags]
    
        for persona in self.filtered_personas:
            item = QListWidgetItem(persona.name)
            self.persona_list.addItem(item)
    
        filtered_prompts = self.prompts if not tag else [p for p in self.prompts if tag in p.tags]
        for prompt in filtered_prompts:
            item = QListWidgetItem(prompt.title)
            item.setData(Qt.UserRole, prompt.id)
            self.prompt_list.addItem(item)

    def try_prompt_in_chatgpt(self):
        prompt_index = self.prompt_list.currentRow()
        if prompt_index < 0:
            QMessageBox.information(self, "Geen prompt geselecteerd", "Selecteer een prompt om te testen.")
            return

        item = self.prompt_list.item(prompt_index)
        prompt_id = item.data(Qt.UserRole)
        prompt = next((p for p in self.prompts if p.id == prompt_id), None)

        if not prompt:
            QMessageBox.warning(self, "Prompt niet gevonden", "De geselecteerde prompt kon niet worden geladen.")
            return

        encoded_prompt = urllib.parse.quote(prompt.content)
        url = f"https://chat.openai.com/?prompt={encoded_prompt}"
        webbrowser.open(url)


    def wrap_in_card(self, widget: QWidget, title: str = None) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        """)
            layout.addWidget(title_label)

        layout.addWidget(widget)

    # Dynamische kleuren afhankelijk van dark mode
        bg_color = '#2d2d2d' if getattr(self, 'is_dark_mode', False) else 'white'
        text_color = '#e0e0e0' if getattr(self, 'is_dark_mode', False) else '#1e293b'
        border_color = '#444' if getattr(self, 'is_dark_mode', False) else '#e5e7eb'

        frame.setStyleSheet(f"""
        QFrame {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: 12px;
            border: 1px solid {border_color};
            padding: 12px;
        }}
    """)

    # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        frame.setGraphicsEffect(shadow)

        return frame