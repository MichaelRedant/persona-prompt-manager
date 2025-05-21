from PySide6.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QListWidgetItem, QPushButton, QMessageBox,
    QApplication, QFrame, QDialog, QLineEdit, QScrollArea, QFileDialog, QGraphicsDropShadowEffect, QSizePolicy, QSystemTrayIcon, QMenu, QGraphicsOpacityEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from models.persona import Persona
from models.prompt import Prompt
from ui.prompt_form import PromptForm
from ui.persona_choice_dialog import PersonaChoiceDialog
from ui.persona_form import PersonaForm
from ui.tag_filter_panel import TagFilterPanel
from datetime import datetime
from ui.ai_mood import determine_ai_mood
from collections import Counter
from ui.prompt_generator import generate_prompt
from ui.prompt_preview_dialog import PromptPreviewDialog
from ui.prompt_wizard import PromptWizardDialog
from services.persona_store import PersonaStore
from services.prompt_store import PromptStore



import json
import os
import webbrowser
import urllib.parse

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QIcon
from ui.click_catcher import ClickCatcherFrame




icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"))



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Persona Vault")
        self.setGeometry(100, 100, 1100, 800)
        self.is_dark_mode = False
    
        # Tray
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)

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
            
                # 📦 Hoofdlayout eerst definiëren
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 🧠 Titel
        title_label = QLabel("🧠 Persona Vault")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 800;
            color: #1e3a8a;
            padding: 32px;
            border-radius: 16px;
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #e0e7ff,
                stop:1 #c7d2fe
            );
        """)

        # Mood ophalen op basis van persona’s
        self.current_mood = determine_ai_mood([])  # leeg bij init
        self.status_chip = QLabel()
        self.status_chip.setAlignment(Qt.AlignRight)
        self.status_chip.setStyleSheet(self.get_chip_style())
        self.status_chip.mousePressEvent = self.show_mood_insights
        self.status_chip.setCursor(Qt.PointingHandCursor)



        # 👋 Subtitel
        subtitle = QLabel("Welkom terug, Michaël — klaar om een nieuwe prompt te bouwen?")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #64748b; margin-top: 0px; margin-bottom: 16px;")

        # 🧭 Header Layout
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.status_chip, alignment=Qt.AlignRight)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle)

        # 📌 Voeg header toe aan layout
        layout.addLayout(header_layout)



    
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
    
        # Persona UI
        self.persona_list = QListWidget()
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
    
        # Prompt UI
        self.prompt_list = QListWidget()
        self.no_prompts_label = QLabel("Geen prompts gevonden.")
        self.no_prompts_label.setAlignment(Qt.AlignCenter)
        self.no_prompts_label.hide()
        prompt_card_widget = self.wrap_in_card(self.prompt_list, "💡 Prompts")
        prompt_wrapper = QVBoxLayout()
        prompt_wrapper.addWidget(self.no_prompts_label)
        prompt_wrapper.addWidget(prompt_card_widget)
        prompt_card_container = QFrame()
        prompt_card_container.setLayout(prompt_wrapper)
    
        from ui.tag_filter_panel import TagFilterPanel
        self.tag_panel = TagFilterPanel(self, self.filter_by_tag)
    
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        top_layout.addWidget(persona_card, 4)
        top_layout.addWidget(prompt_card_container, 3)
        top_layout.addWidget(self.tag_panel, 2)
    
        # Prompttekst
        self.prompt_details_box = QTextEdit()
        self.prompt_details_box.setReadOnly(True)
        self.prompt_details_box.setMinimumHeight(200)
        prompt_card = self.wrap_in_card(self.prompt_details_box, "✏️ Prompttekst")
    
        # Interactieknoppen
        self.copy_prompt_button = QPushButton("📋 Kopieer prompt")
        self.copy_prompt_button.clicked.connect(self.copy_prompt)
        self.copy_prompt_button.setCursor(Qt.PointingHandCursor)
        self.copy_prompt_button.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        
        
        
        self.prompt_info_label = QLabel()
        self.prompt_info_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        self.prompt_info_label.setWordWrap(True)
        self.prompt_tip_label = QLabel("💡 Tip: Start prompts met een duidelijke rol, zoals \"Je bent een expert copywriter...\"")
        self.prompt_tip_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        self.prompt_tip_label.setWordWrap(True)
        self.try_prompt_button = QPushButton("🧪 Test prompt in ChatGPT")
        self.try_prompt_button.clicked.connect(self.try_prompt_in_chatgpt)
        self.try_prompt_button.setCursor(Qt.PointingHandCursor)
        self.try_prompt_button.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
        """)
        # ➕ Genereer Prompt-knop
        self.generate_prompt_button = QPushButton("🎛️ Genereer Prompt")
        self.generate_prompt_button.clicked.connect(self.open_prompt_wizard)
        self.generate_prompt_button.setCursor(Qt.PointingHandCursor)
        self.generate_prompt_button.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)

        test_button_box = QVBoxLayout()
        test_button_box.setSpacing(10)

        test_button_box.addWidget(self.copy_prompt_button)
        test_button_box.addWidget(self.prompt_info_label)
        test_button_box.addWidget(self.prompt_tip_label)

        # ➕ Voeg Genereer Prompt-knop toe vóór de Test-knop
        test_button_box.addWidget(self.generate_prompt_button)
        test_button_box.addWidget(self.try_prompt_button)

        test_button_box.addStretch()

        test_card = QFrame()
        test_card.setLayout(test_button_box)
        test_card.setStyleSheet("background-color: transparent;")
    
        prompt_row = QHBoxLayout()
        prompt_row.setSpacing(20)
        prompt_row.addWidget(prompt_card, 5)
        prompt_row.addWidget(test_card, 3)
    
        # Beschrijving
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setMinimumHeight(100)
    
        self.prompt_metadata_label = QLabel()
        self.prompt_metadata_label.setStyleSheet("font-size: 12px; color: #6b7280; padding-left: 12px; padding-top: 4px;")
    
        self.add_persona_button = QPushButton("➕ Nieuwe Persona")
        self.edit_persona_button = QPushButton("✏️ Bewerken Persona")
        self.delete_persona_button = QPushButton("❌ Verwijderen Persona")
        self.favorite_button = QPushButton("⭐ Toggle Favoriet")
    
        persona_btns = QHBoxLayout()
        persona_btns.addWidget(self.add_persona_button)
        persona_btns.addWidget(self.edit_persona_button)
        persona_btns.addWidget(self.delete_persona_button)
        persona_btns.addWidget(self.favorite_button)
    
        self.add_prompt_button = QPushButton("➕ Nieuwe Prompt")
        self.edit_prompt_button = QPushButton("✏️ Bewerken Prompt")
        self.delete_prompt_button = QPushButton("❌ Verwijderen Prompt")
    
        prompt_btns = QHBoxLayout()
        prompt_btns.addWidget(self.add_prompt_button)
        prompt_btns.addWidget(self.edit_prompt_button)
        prompt_btns.addWidget(self.delete_prompt_button)
       
    
        # Layout opbouw
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.addLayout(search_row)
        layout.addLayout(top_layout)
        layout.addLayout(prompt_row)
        layout.addWidget(self.wrap_in_card(self.details_box, "🧠 Beschrijving"))
        layout.addWidget(self.prompt_metadata_label)
        layout.addLayout(persona_btns)
        layout.addLayout(prompt_btns)
    
        container_widget = QWidget()
        container_widget.setLayout(layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)
        self.setCentralWidget(scroll_area)
    
        # Events
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
    
        self.click_catcher = ClickCatcherFrame(self, self.clear_selections)
        self.click_catcher.setGeometry(self.rect())
        self.click_catcher.raise_()
        self.click_catcher.lower()
    
        # Data
         # ✅ Services initialiseren
        self.persona_store = PersonaStore()
        self.prompt_store = PromptStore()

        # ✅ Data laden
        self.load_data()

        # ✅ UI updaten
        self.update_status_chip()
        self.update_moodchip_tooltip()

        # ✅ Laatste visuele updates
        self.showMaximized()
    
        # Button Effects (zorg dat deze functie bestaat!)
        self.apply_button_effects(self.copy_prompt_button, "#4f46e5", "#4338ca")
        self.apply_button_effects(self.try_prompt_button, "#16a34a", "#15803d")



    def load_data(self):
           try:
               self.personas = self.persona_store.load()
           except Exception as e:
               QMessageBox.critical(self, "Fout bij laden persona's", str(e))
               self.personas = []

           try:
               self.prompts = self.prompt_store.load()
           except Exception as e:
               QMessageBox.critical(self, "Fout bij laden prompts", str(e))
               self.prompts = []

           self.refresh_persona_list()
           self.update_persona_title()
           self.tag_panel.update_tags(self.personas, self.prompts)
           self.update_status_chip()
           self.update_moodchip_tooltip()

           # ⚙️ Selecteer eerste persona (indien aanwezig)
           if self.persona_list.count() > 0:
               self.persona_list.setCurrentRow(0)
               self.display_persona_details(0)


    def load_personas(self):
        try:
            self.personas = self.persona_store.load()
        except RuntimeError as e:
            QMessageBox.critical(self, "Fout bij laden", str(e))
            self.personas = []

       # UI bijwerken
        self.refresh_persona_list()
        self.update_persona_title()
        self.tag_panel.update_tags(self.personas, self.prompts)
        self.update_status_chip()
        self.update_moodchip_tooltip()

        # FIX: selecteer eerste persona om prompts te tonen
        if self.persona_list.count() > 0:
            self.persona_list.setCurrentRow(0)
            self.display_persona_details(0)



    def save_prompts(self):
        try:
            self.prompt_store.save(self.prompts)
        except RuntimeError as e:
            QMessageBox.critical(self, "Fout bij opslaan", str(e))

            

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
    "💡 Tip: Voeg beperkingen toe: 'Gebruik maximaal 100 woorden'",
    "💡 Tip: Geef een format op: 'Antwoord in een lijst met emoji's'",
    "💡 Tip: Vraag GPT om te denken: 'Denk stap voor stap na over dit probleem'",
    "💡 Tip: Laat GPT zich verplaatsen in een rol: 'Je bent een recruiter die...'",
    "💡 Tip: Voeg voorbeelddata toe in je prompt voor betere output",
    "💡 Tip: Benoem wat je niet wilt: 'Vermijd overdreven technische termen'",
    "💡 Tip: Gebruik tone of voice: 'Schrijf in een informele, enthousiaste stijl'",
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
        self.no_personas_label.setVisible(False)
    
        self.filtered_personas = sorted(
            self.personas,
            key=lambda p: (not p.is_favorite, p.name.lower())
        )
    
        for persona in self.filtered_personas:
            label = f"⭐ {persona.name}" if persona.is_favorite else f"☆ {persona.name}"
            item = QListWidgetItem(label)
            self.persona_list.addItem(item)
    
        self.no_personas_label.setVisible(len(self.filtered_personas) == 0)
    
        # 👇 Voeg dit toe om bij opstart automatisch de eerste te tonen
        if self.filtered_personas:
            self.persona_list.setCurrentRow(0)
            self.display_persona_details(0)




    def add_prompt(self):
        selected_persona = None
        persona_index = self.persona_list.currentRow()

        if 0 <= persona_index < self.persona_list.count():
            selected_persona = (
                self.filtered_personas[persona_index]
                if hasattr(self, 'filtered_personas') and self.filtered_personas
                else self.personas[persona_index]
            )

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

            self.prompt_store.save(self.prompts)


            # Toon opnieuw de juiste persona details
            if selected_persona:
                match_index = next((i for i, p in enumerate(self.personas) if p.id == selected_persona.id), -1)
                if match_index != -1:
                    self.display_persona_details(match_index)

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
            updated_prompt = dialog.get_prompt()
            if not updated_prompt:
                return

            # ✅ Vervang de oude prompt door de nieuwe
            for i, p in enumerate(self.prompts):
                if p.id == updated_prompt.id:
                    self.prompts[i] = updated_prompt
                    break

            # ✅ Schrijf weg
            self.prompt_store.save(self.prompts)


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

            self.prompt_store.save(self.prompts)

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
            if persona_form.exec():
                new_persona = persona_form.get_persona()
                self.personas.append(new_persona)
                self.persona_store.save(self.personas)
                self.refresh_persona_list()
                self.update_status_chip()
                self.update_moodchip_tooltip()
                self.tag_panel.update_tags(self.personas, self.prompts)

        elif result == 2:
            wizard = PromptWizardDialog(self)
            wizard.exec()



    def edit_persona(self):
        index = self.persona_list.currentRow()
        if index < 0:
            return
        persona = self.filtered_personas[index] if hasattr(self, 'filtered_personas') else self.personas[index]
        dialog = PersonaForm(self, persona)
        if dialog.exec():
            updated = dialog.get_persona()
            self.personas[index] = updated
            self.persona_store.save(self.personas)
            self.refresh_persona_list()
            self.update_status_chip()
            self.update_moodchip_tooltip()
            self.update_persona_title()
            self.persona_list.setCurrentRow(index)
            self.tag_panel.update_tags(self.personas, self.prompts)


    def delete_persona(self):
        index = self.persona_list.currentRow()
        if index < 0:
            return
        persona = self.filtered_personas[index] if hasattr(self, 'filtered_personas') else self.personas[index]
        reply = QMessageBox.question(
            self, "Bevestigen",
            f"Ben je zeker dat je '{persona.name}' wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.personas = [p for p in self.personas if p.id != persona.id]
            self.persona_store.save(self.personas)
            self.refresh_persona_list()
            self.update_status_chip()
            self.update_moodchip_tooltip()
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
        self.persona_store.save(self.personas)


        self.refresh_persona_list()
        
    def toggle_favorite_by_click(self, item: QListWidgetItem):
        index = self.persona_list.row(item)
        if index < 0 or not hasattr(self, 'filtered_personas'):
            return

        persona = self.filtered_personas[index]
        persona.is_favorite = not persona.is_favorite

    # Opslaan
        self.persona_store.save(self.personas)


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
            self.persona_store.save(self.personas)
            self.refresh_persona_list()

    def add_template_persona(self):
        from ui.persona_form import PersonaForm
        dialog = PersonaForm(self, persona=None, template_mode=True)
        if dialog.exec():
            new_persona = dialog.get_persona()
            self.personas.append(new_persona)
            self.persona_store.save(self.personas)
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

        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(widget)

        # Kleur & stijl
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

        # Schaduw
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        frame.setGraphicsEffect(shadow)

        return frame  # ⬅️ deze return is CRUCIAAL!



    def update_status_chip(self):
        self.current_mood = determine_ai_mood(self.personas)
        self.status_chip.setText(f"{self.current_mood['emoji']} {self.current_mood['label']}")
        self.status_chip.setStyleSheet(self.get_chip_style())

    def get_chip_style(self):
        mood = self.current_mood
        return f"""
            background-color: {mood['bg']};
            color: {mood['fg']};
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        """
    
    def update_moodchip_tooltip(self):
        if not hasattr(self, 'personas') or not self.personas:
            self.status_chip.setToolTip("Nog geen persona’s aanwezig.")
            return

        # Verzamel alle tags
        all_tags = [tag for p in self.personas for tag in p.tags]
        if not all_tags:
            self.status_chip.setToolTip("Nog geen tags toegevoegd aan persona’s.")
            return

        # Top 3 tags
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(3)
        tag_list = ", ".join(tag for tag, _ in top_tags)

        tooltip_text = f"""💡 AI Mood wordt gegenereerd o.b.v. je actieve persona’s.\nTop 3 tags: {tag_list}"""
        self.status_chip.setToolTip(tooltip_text)


    def show_mood_insights(self, event):
        if hasattr(self, 'mood_popup') and self.mood_popup is not None:
            self.mood_popup.close()
            self.mood_popup = None

        mood = self.current_mood.get('label', "Onbekend")
        mood_emoji = self.current_mood.get('emoji', "💡")
        insights = {
            "Creatieve Flow": [
                "🎨 Je AI mood is sterk creatief.",
                "🧠 Persona's in design en UI/UX.",
                "✨ Gebruik visueel geïnspireerde prompts."
            ],
            "Strategisch Denken": [
                "📊 Analyse en planning staan centraal.",
                "🧠 Data-gedreven persona’s aanwezig.",
                "📈 Combineer met optimalisatie-prompts."
            ],
            "Innovatief": [
                "🚀 Je team straalt technologie uit.",
                "🤖 AI, automation en innovatie-tags.",
                "🔬 Combineer met experimenterende prompts."
            ],
            "Empathisch": [
                "🤝 Focus op interpersoonlijke thema’s.",
                "🧘 Persona’s in coaching en zorg.",
                "💬 Gebruik zachtere, human-centered prompts."
            ],
            "Gebalanceerde Mix": [
                "🧩 Divers persona-aanbod.",
                "🎯 Geen dominante richting, veelzijdig inzetbaar.",
                "🎛️ Test verschillende strategieën."
            ],
            "GPT paraat": [
                "💡 Geen specifieke richting gedetecteerd.",
                "📥 Voeg persona’s toe om mood te activeren.",
                "🧪 Tip: gebruik tags en categorieën."
            ]
        }

        popup = QFrame(self)
        popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        popup.setObjectName("moodPopup")
        popup.setStyleSheet("""
        QFrame#moodPopup {
            background-color: rgba(255, 255, 255, 0.75);
            border-radius: 16px;
            border: 1px solid rgba(229, 231, 235, 0.6);
            backdrop-filter: blur(16px); /* dit werkt enkel in Web-technologie, NIET in Qt */
        }
        QLabel {
            color: #1e293b;
            font-size: 13px;
            padding: 4px 10px;
        }
        QLabel#title {
            font-size: 15px;
            font-weight: bold;
            color: #1d4ed8;
            padding-top: 8px;
        }
    """)


        layout = QVBoxLayout(popup)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(6)

        title = QLabel(f"{mood_emoji} {mood}")
        title.setObjectName("title")
        layout.addWidget(title)

        for line in insights.get(mood, ["ℹ️ Geen inzichten beschikbaar."]):
            lbl = QLabel(line)
            layout.addWidget(lbl)

        popup.adjustSize()

        # 📍 Positionering: onder de chip, uitgelijnd rechts met het main window
        chip_pos = self.status_chip.mapToGlobal(self.status_chip.rect().bottomRight())
        window_right = self.mapToGlobal(self.rect().topRight()).x()
        popup_width = popup.sizeHint().width()

        margin = 12
        x = window_right - popup_width - margin
        y = chip_pos.y() + 8

        popup.move(x, y)

        # 🎞️ Fade-in
        opacity_effect = QGraphicsOpacityEffect(popup)
        popup.setGraphicsEffect(opacity_effect)
        fade_in = QPropertyAnimation(opacity_effect, b"opacity", popup)
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        fade_in.start()

        # Schaduw
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 60))
        popup.setGraphicsEffect(shadow)

        popup.show()
        self.mood_popup = popup

        # 🕐 Automatische sluiting
        def fade_out_and_close():
            fade_out = QPropertyAnimation(opacity_effect, b"opacity", popup)
            fade_out.setDuration(400)
            fade_out.setStartValue(1)
            fade_out.setEndValue(0)
            fade_out.setEasingCurve(QEasingCurve.InOutCubic)
            fade_out.finished.connect(popup.close)
            fade_out.start()

        QTimer.singleShot(6000, fade_out_and_close)






    
    def apply_button_effects(self, button, base_color: str, hover_color: str):
        # Schaduw
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 80))
        button.setGraphicsEffect(shadow)
    
        # Animatie
        anim = QPropertyAnimation(button, b"styleSheet")
        anim.setDuration(250)
        anim.setEasingCurve(QEasingCurve.OutCubic)
    
        # Basisstijl
        normal_style = f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
        button.setStyleSheet(normal_style)
        
    def open_prompt_wizard(self):
        wizard = PromptWizardDialog(self)
        wizard.exec()    
        
    def show_prompt_preview(self):
        # Stap 1: Haal geselecteerde persona
        index = self.persona_list.currentRow()
        if index < 0 or not hasattr(self, 'filtered_personas'):
            QMessageBox.information(self, "Geen selectie", "Selecteer eerst een persona.")
            return

        persona = self.filtered_personas[index]

        # Stap 2: Genereer prompt
        from ui.prompt_generator import generate_prompt
        generated = generate_prompt(persona)

        # Stap 3: Toon in modale dialoog
        dlg = QDialog(self)
        dlg.setWindowTitle(f"🎛️ Gegenereerde Prompt voor {persona.name}")
        dlg.setMinimumSize(700, 500)

        layout = QVBoxLayout(dlg)

        # Prompt Preview
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setText(generated)
        preview.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout.addWidget(preview)

        # Kopieerknop
        copy_btn = QPushButton("📋 Kopieer prompt")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(generated))
        layout.addWidget(copy_btn)

        # Sluitknop
        close_btn = QPushButton("❌ Sluiten")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)
        dlg.exec()

    
        
    def preview_generated_from_prompt(self):
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Selecteer een prompt", "Selecteer een prompt om de gegenereerde versie te bekijken.")
            return

        prompt_id = current_item.data(Qt.UserRole)
        prompt = next((p for p in self.prompts if p.id == prompt_id), None)
        if not prompt:
            QMessageBox.warning(self, "Fout", "Kon de prompt niet laden.")
            return

        # Bijhorende persona zoeken
        persona = next((p for p in self.personas if p.id == prompt.persona_id), None)
        if not persona:
            QMessageBox.warning(self, "Geen persona", "Deze prompt is niet gekoppeld aan een geldige persona.")
            return

        # Prompt genereren
        generated = generate_prompt(persona)

        # Toon in dialoog
        dlg = QDialog(self)
        dlg.setWindowTitle("🎛️ Gegenereerde Prompt")
        dlg.setMinimumSize(700, 500)
        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(generated)
        layout.addWidget(text)

        # Knop om te kopiëren
        copy_btn = QPushButton("📋 Kopieer naar klembord")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(generated))
        layout.addWidget(copy_btn)

        dlg.setLayout(layout)
        dlg.exec()