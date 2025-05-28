# UI & Qt
from PySide6.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QListWidgetItem, QPushButton, QMessageBox,
    QApplication, QFrame, QDialog, QLineEdit,
    QSystemTrayIcon, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QIcon
from collections import Counter
from datetime import datetime
import json, os

# Models
from models.persona import Persona
from models.prompt import Prompt

# Services
from services.persona_store import PersonaStore
from services.prompt_store import PromptStore
from services.export_utils import export_personas, export_prompts  

# UI modules
from ui.main_layout import build_main_layout
from ui.menu_actions import bind_menu_actions
from ui.main_logic import *
from ui.main_events import bind_event_handlers
from ui.main_components import wrap_in_card
from ui.style_utils import apply_button_effects 
from ui.tag_filter_panel import TagFilterPanel
from ui.prompt_wizard import PromptWizardDialog
from ui.prompt_generator import generate_prompt
from ui.click_catcher import ClickCatcherFrame
from ui.persona_dashboard import PersonaDashboard
from ui.persona_form import PersonaForm
from ui.theme_utils import toggle_dark_mode
from ui.style_utils import apply_button_effects
from ui.main_logic import display_persona_details
# Andere
from logic.ai_mood import determine_ai_mood
from ui.main_events import bind_event_handlers

icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Persona Vault")
        self.setGeometry(100, 100, 1100, 800)
        self.is_dark_mode = False

        # Tray icoon
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray_icon.setToolTip("Persona Vault")
        tray_menu = QMenu()
        tray_menu.addAction("Sluiten", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 🔧 Eerst layout bouwen: buttons worden hier gedefinieerd
        self.layout, self.scroll_area = build_main_layout(self)
        print("🔍 Na build_main_layout:")
        print("👁️‍🗨️ add_persona_button zichtbaar?", self.add_persona_button.isVisible())
        print("👁️‍🗨️ edit_persona_button zichtbaar?", self.edit_persona_button.isVisible())
        print("👁️‍🗨️ delete_persona_button zichtbaar?", self.delete_persona_button.isVisible())
        print("👁️‍🗨️ favorite_button zichtbaar?", self.favorite_button.isVisible())
        self.add_persona_button.show()
        self.edit_persona_button.show()
        self.delete_persona_button.show()
        self.favorite_button.show()


        # ✅ Daarna pas de knoppen logica koppelen
        self.display_persona_details = display_persona_details.__get__(self)
        
        bind_event_handlers(self)
        
        # 🎛️ En daarna menu activeren
        bind_menu_actions(self, self.menuBar())

    
        # Events
        self.persona_dashboard.persona_selected.connect(self.display_persona_details)
        self.persona_dashboard.favorite_toggled.connect(self.toggle_favorite)
        self.prompt_list.itemSelectionChanged.connect(lambda: self.display_prompt_details(self.prompt_list.currentRow()))
        self.search_input.textChanged.connect(self.perform_search)
        self.edit_prompt_button.clicked.connect(self.edit_prompt)
        self.delete_prompt_button.clicked.connect(self.delete_prompt)
        self.copy_prompt_button.clicked.connect(self.copy_prompt)
        self.add_persona_button.clicked.connect(self.add_persona)
        self.edit_persona_button.clicked.connect(self.edit_persona)
        self.delete_persona_button.clicked.connect(self.delete_persona)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.persona_dashboard.persona_selected.connect(self.check_selection_state)
        

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
        
        # ✅ Persona Dashboard events koppelen NA alle methodes geladen zijn
        bind_persona_dashboard_events(self)

        # ✅ Laatste visuele updates
        self.showMaximized()
        
        if hasattr(self, 'copy_prompt_button'):
            apply_button_effects(self.copy_prompt_button, "#4f46e5", "#4338ca")
        if hasattr(self, 'try_prompt_button'):
            apply_button_effects(self.try_prompt_button, "#16a34a", "#15803d")
        

    def load_data(self):
        try:
            self.personas = self.persona_store.load()
            print(f"✅ Personas geladen: {[p.name for p in self.personas]}")
        except Exception as e:
            QMessageBox.critical(self, "Fout bij laden persona's", str(e))
            self.personas = []
            
        self.selected_persona_index = None
            
        self.filtered_personas = self.personas.copy()
        try:
            self.prompts = self.prompt_store.load()
            print(f"✅ Prompts geladen: {[p.title for p in self.prompts]}")
        except Exception as e:
            QMessageBox.critical(self, "Fout bij laden prompts", str(e))
            self.prompts = []
            
        
        self.refresh_persona_list()
        self.update_persona_title()
        self.tag_panel.update_tags(self.personas, self.prompts)
        self.update_status_chip()
        self.update_moodchip_tooltip()
        if hasattr(self, 'persona_dashboard'):
            self.persona_dashboard.refresh(self.filtered_personas)
        if self.filtered_personas:
            print("🔁 Initialiseer persona view met index 0")
            self.persona_dashboard.list.setCurrentRow(0)
            self.display_persona_details(0)

    def copy_prompt(self):
        print("⚠️ copy_prompt nog niet geïmplementeerd")

    def delete_prompt(self):
        print("⚠️ delete_prompt nog niet geïmplementeerd")

    def edit_prompt(self):
        print("⚠️ edit_prompt nog niet geïmplementeerd")
        
    def try_prompt_in_chatgpt(self):
        print("⚠️ try_prompt_in_chatgpt() is nog niet geïmplementeerd.")
        



    def load_data(self):
        try:
            self.personas = self.persona_store.load()
            print(f"✅ Personas geladen: {[p.name for p in self.personas]}")
        except Exception as e:
            QMessageBox.critical(self, "Fout bij laden persona's", str(e))
            self.personas = []
    
        self.selected_persona_index = None
        self.filtered_personas = self.personas.copy()
    
        try:
            self.prompts = self.prompt_store.load()
            print(f"✅ Prompts geladen: {[p.title for p in self.prompts]}")
        except Exception as e:
            QMessageBox.critical(self, "Fout bij laden prompts", str(e))
            self.prompts = []
    
        self.refresh_persona_list()
        self.update_persona_title()
        self.tag_panel.update_tags(self.personas, self.prompts)
        self.update_status_chip()
        self.update_moodchip_tooltip()
    
        if hasattr(self, 'persona_dashboard'):
            self.persona_dashboard.refresh(self.filtered_personas)
    
        # ✅ Toon eerste persona automatisch
        if self.filtered_personas:
            self.display_persona_details(0)



    def save_prompts(self):
        try:
            self.prompt_store.save(self.prompts)
        except RuntimeError as e:
            QMessageBox.critical(self, "Fout bij opslaan", str(e))
    
    
    def update_persona_title(self):
        count = len(self.filtered_personas) if hasattr(self, 'filtered_personas') else len(self.personas)
        if hasattr(self.persona_dashboard, "title"):
           self.persona_dashboard.title.setText(f"📊 Persona Dashboard ({count})")

            
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
 
      
        
    def show_prompt_preview(self):
        # Stap 1: Haal geselecteerde persona
        index = self.persona_dashboard.list.currentRow()
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