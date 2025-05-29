from PySide6.QtWidgets import (
    QMessageBox, QListWidgetItem, QFrame, QVBoxLayout,
    QLabel, QApplication, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QDialog, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation 
from PySide6.QtGui import QColor
from ui.persona_form import PersonaForm
from ui.prompt_form import PromptForm
from ui.prompt_wizard import PromptWizardDialog
from ui.persona_choice_dialog import PersonaChoiceDialog
import urllib.parse
import webbrowser
from ui.main_logic import (
    display_persona_details,
    display_prompt_details,
    refresh_persona_list,
    perform_search,
    check_prompt_selection,
    clear_selections
)
from ui.persona_card import PersonaCard

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
    index = self.selected_persona_index
    if index is None or index < 0 or index >= len(self.filtered_personas):
        return
    persona = self.filtered_personas[index]
    dialog = PersonaForm(self, persona)
    if dialog.exec():
        updated = dialog.get_persona()
        self.personas = [
            updated if p.id == persona.id else p for p in self.personas
        ]
        self.persona_store.save(self.personas)
        self.refresh_persona_list()
        self.update_status_chip()
        self.update_moodchip_tooltip()
        self.update_persona_title()
        self.display_persona_details(index)
        self.tag_panel.update_tags(self.personas, self.prompts)


        
def delete_persona(self):
    index = self.selected_persona_index
    if index is None or index < 0 or index >= len(self.filtered_personas):
        return
    persona = self.filtered_personas[index]
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


          
def toggle_search_input(self):
        self.search_input.setVisible(not self.search_input.isVisible())
        if self.search_input.isVisible():
            self.search_input.setFocus()
        else:
            self.search_input.clear()
            self.perform_search("")

def toggle_favorite(self, index=None):
    index = index if index is not None else self.selected_persona_index
    if index is None or index < 0 or index >= len(self.filtered_personas):
        return
    persona = self.filtered_personas[index]
    persona.is_favorite = not persona.is_favorite
    self.persona_store.save(self.personas)
    self.refresh_persona_list()


    
def toggle_favorite_by_click(self, index):
    if index < 0 or not hasattr(self, 'filtered_personas'):
        return
    persona = self.filtered_personas[index]
    persona.is_favorite = not persona.is_favorite
    self.persona_store.save(self.personas)
    self.refresh_persona_list()

        
def add_prompt(self):
    selected_persona = None
    persona_index = self.selected_persona_index

    if persona_index is not None and 0 <= persona_index < len(self.filtered_personas):
        selected_persona = self.filtered_personas[persona_index]
    else:
        selected_persona = None

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
        QMessageBox.information(self, "Geen selectie", "Selecteer een prompt om te bewerken.")
        return

    prompt_id = current_item.data(Qt.UserRole)
    prompt = next((p for p in self.prompts if p.id == prompt_id), None)
    if not prompt:
        QMessageBox.warning(self, "Fout", "Kan de geselecteerde prompt niet vinden.")
        return

    dialog = PromptForm(
        self,
        prompt=prompt,
        personas=self.personas,
        preselected_persona=next((p for p in self.personas if p.id == prompt.persona_id), None)
    )

    if dialog.exec():
        updated_prompt = dialog.get_prompt()
        if not updated_prompt:
            return

        # Prompt vervangen
        index = next((i for i, p in enumerate(self.prompts) if p.id == prompt.id), -1)
        if index != -1:
            self.prompts[index] = updated_prompt
            self.prompt_store.save(self.prompts)

        # Interface updaten
        persona_index = self.selected_persona_index
        if persona_index is not None:
            self.display_persona_details(persona_index)

        self.tag_panel.update_tags(self.personas, self.prompts)


def delete_prompt(self):
    current_item = self.prompt_list.currentItem()
    if not current_item:
        QMessageBox.information(self, "Geen selectie", "Selecteer een prompt om te verwijderen.")
        return

    prompt_id = current_item.data(Qt.UserRole)
    prompt = next((p for p in self.prompts if p.id == prompt_id), None)
    if not prompt:
        QMessageBox.warning(self, "Fout", "Kan de geselecteerde prompt niet vinden.")
        return

    confirm = QMessageBox.question(
        self,
        "Bevestig verwijderen",
        f"Weet je zeker dat je de prompt '{prompt.title}' wilt verwijderen?",
        QMessageBox.Yes | QMessageBox.No
    )

    if confirm == QMessageBox.Yes:
        self.prompts = [p for p in self.prompts if p.id != prompt_id]
        self.prompt_store.save(self.prompts)

        # Interface updaten
        persona_index = self.selected_persona_index
        if persona_index is not None:
            self.display_persona_details(persona_index)

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

def filter_by_tag(self, tag):
    self.persona_dashboard.clear_personas()
    self.prompt_list.clear()
    self.details_box.clear()
    self.prompt_details_box.clear()

    if not tag:
        self.filtered_personas = self.personas.copy()
    else:
        self.filtered_personas = [p for p in self.personas if tag in p.tags]

    for index, persona in enumerate(self.filtered_personas):
        card = PersonaCard(index=index, persona=persona)
        card.clicked.connect(self.display_persona_details)
        card.toggled_favorite.connect(self.toggle_favorite_by_click)
        self.persona_dashboard.scroll_layout.addWidget(card)

    # Filter prompts ook
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
    
def show_mood_insights(self, event):
        if hasattr(self, 'mood_popup') and self.mood_popup is not None:
            self.mood_popup.close(  )
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
        shadow.setColor(QColor(0, 0, 0,  60))
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
        
def show_about(main):
    dialog = QDialog(main)
    dialog.setWindowTitle("ℹ️ Over Persona Vault")
    dialog.setMinimumSize(400, 280)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #f9fafb;
            border-radius: 16px;
        }
        QLabel {
            font-size: 14px;
            color: #1e293b;
        }
        QPushButton {
            background-color: #4f46e5;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #4338ca;
        }
    """)

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    label = QLabel("🎯 <b>Persona Vault</b> v1.0.0<br><br>"
                   "Beheer, bewerk en gebruik je AI persona’s en prompts op een krachtige manier.<br><br>"
                   "🔧 Gemaakt door Michaël Redant met ❤️ en ChatGPT.<br>"
                   "💡 Ideeën, feedback of bugs? Laat het weten!")
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    close_btn = QPushButton("Sluiten")
    close_btn.clicked.connect(dialog.accept)
    layout.addWidget(close_btn, alignment=Qt.AlignCenter)

    dialog.exec()
    
def open_prompt_wizard(self):
    wizard = PromptWizardDialog(self)
    wizard.exec()  
        
        
def bind_event_handlers(main):
    # Persona events
    main.add_persona = add_persona.__get__(main)
    main.edit_persona = edit_persona.__get__(main)
    main.delete_persona = delete_persona.__get__(main)
    main.toggle_favorite = toggle_favorite.__get__(main)
    main.toggle_favorite_by_click = toggle_favorite_by_click.__get__(main)

    main.add_persona_button.clicked.connect(main.add_persona)
    main.edit_persona_button.clicked.connect(main.edit_persona)
    main.delete_persona_button.clicked.connect(main.delete_persona)
    main.favorite_button.clicked.connect(main.toggle_favorite)

    # Prompt events
    main.add_prompt = add_prompt.__get__(main)
    main.edit_prompt = edit_prompt.__get__(main)
    main.delete_prompt = delete_prompt.__get__(main)
    main.copy_prompt = copy_prompt.__get__(main)

    main.add_prompt_button.clicked.connect(main.add_prompt)
    main.edit_prompt_button.clicked.connect(main.edit_prompt)
    main.delete_prompt_button.clicked.connect(main.delete_prompt)
    main.copy_prompt_button.clicked.connect(main.copy_prompt)

    # Extra functionaliteit
    main.toggle_search_input = toggle_search_input.__get__(main)
    main.try_prompt_in_chatgpt = try_prompt_in_chatgpt.__get__(main)
    main.open_prompt_wizard = open_prompt_wizard.__get__(main)
    main.filter_by_tag = filter_by_tag.__get__(main)
    main.show_mood_insights = show_mood_insights.__get__(main)

    main.search_toggle_button.clicked.connect(main.toggle_search_input)
    main.tag_panel.tag_clicked.connect(main.filter_by_tag)
    
    main.display_persona_details = display_persona_details.__get__(main)
    main.display_prompt_details = display_prompt_details.__get__(main)
    main.refresh_persona_list = refresh_persona_list.__get__(main)
    main.perform_search = perform_search.__get__(main)
    main.clear_selections = clear_selections.__get__(main)
    main.check_prompt_selection = check_prompt_selection.__get__(main)
