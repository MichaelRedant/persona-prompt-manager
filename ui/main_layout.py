from PySide6.QtWidgets import QVBoxLayout, QWidget, QScrollArea
from ui.main_components import build_components

def build_main_layout(self):
    layout, scroll_area = build_components(self)
    self.setCentralWidget(scroll_area)
    return layout, scroll_area

