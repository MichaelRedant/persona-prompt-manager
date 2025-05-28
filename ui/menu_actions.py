# ui/menu_actions.py
from PySide6.QtWidgets import QMenuBar
from services.export_utils import export_personas, export_prompts
from ui.main_events import show_about


def bind_menu_actions(self, menu_bar: QMenuBar):
    file_menu = menu_bar.addMenu("Bestand")
    file_menu.addAction("Exporteer persona's").triggered.connect(lambda: export_personas(self))
    file_menu.addAction("Exporteer prompts").triggered.connect(lambda: export_prompts(self))
    file_menu.addAction("Afsluiten").triggered.connect(self.close)

    edit_menu = menu_bar.addMenu("Bewerken")
    edit_menu.addAction("Nieuwe Persona").triggered.connect(self.add_persona)
    edit_menu.addAction("Nieuwe Prompt").triggered.connect(self.add_prompt)

    help_menu = menu_bar.addMenu("Help")
    help_menu.addAction("Over").triggered.connect(lambda: show_about(self))
