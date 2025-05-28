from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt
from logic.helpers import (
    find_persona_by_id,
    find_prompt_by_id,
    get_related_prompts,
    format_persona_description,
    format_prompt_metadata
)
import random
def display_persona_details(self, index):
   print("✅ display_persona_details werd uitgevoerd met index:", index)
   self.selected_persona_index = index
   # 👁️ Knoppen altijd tonen
   self.add_persona_button.show()
   self.edit_persona_button.show()
   self.delete_persona_button.show()
   self.favorite_button.show()
   self.add_prompt_button.show()
   if not hasattr(self, 'filtered_personas') or index < 0 or index >= len(self.filtered_personas):
       self.details_box.clear()
       self.prompt_list.clear()
       self.prompt_details_box.clear()
       return
   persona = self.filtered_personas[index]
   self.details_box.setPlainText(format_persona_description(persona))
   self.prompt_list.clear()
   related_prompts = get_related_prompts(self.prompts, persona.id)
   for prompt in related_prompts:
       item = QListWidgetItem(prompt.title)
       item.setData(Qt.UserRole, prompt.id)
       self.prompt_list.addItem(item)
   if self.prompt_list.count() > 0:
       self.prompt_list.setCurrentRow(0)
       self.display_prompt_details(0)

def display_prompt_details(self, index):
    if index >= 0:
        item = self.prompt_list.item(index)
        prompt_id = item.data(Qt.UserRole)
        prompt = find_prompt_by_id(self.prompts, prompt_id)

        if prompt:
            self.edit_prompt_button.show()
            self.delete_prompt_button.show()
            self.copy_prompt_button.show()

            persona = find_persona_by_id(self.personas, prompt.persona_id)
            persona_name = persona.name if persona else "Ongekend"

            self.prompt_info_label.setText(format_prompt_metadata(prompt, persona_name))
            self.prompt_tip_label.setText(random.choice([
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
            ]))

            self.prompt_details_box.setPlainText(prompt.content)

            if persona:
                self.details_box.setPlainText(format_persona_description(persona))

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
    self.filtered_personas = sorted(
        self.personas,
        key=lambda p: (not p.is_favorite, p.name.lower())
    )
    if hasattr(self, 'persona_dashboard'):
        self.persona_dashboard.refresh(self.filtered_personas)

    if self.filtered_personas:
        self.display_persona_details(0)
        
def perform_search(self, query: str):
        query = query.lower().strip()

        self.persona_dashboard.list.clear()
        self.prompt_list.clear()
        self.details_box.clear()
        self.prompt_details_box.clear()
        self.update_persona_title()

        self.filtered_personas = []
        self.filtered_prompts = []


    # Zoek in persona's
        for persona in self.personas:
            persona_text = " ".join([
                persona.name,
                persona.category,
                " ".join(persona.tags)
            ]).lower()

            if query in persona_text:
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
            
def check_selection_state(self, index=None):
        if index is None or index < 0:
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
    self.persona_dashboard.list.clearSelection()
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
    
def bind_persona_dashboard_events(self):
    self.persona_dashboard.persona_selected.connect(self.display_persona_details)
    self.persona_dashboard.favorite_toggled.connect(self.toggle_favorite)

