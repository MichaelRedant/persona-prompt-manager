# ui/prompt_dashboard.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from ui.prompt_card import PromptCard
from models.prompt import Prompt


class PromptDashboard(QWidget):
    prompt_selected = Signal(int)

    def __init__(self, parent=None, prompts=None):
        super().__init__(parent)
        self.prompts = prompts or []

        self.setObjectName("promptDashboard")
        self.setStyleSheet("""
            QWidget#promptDashboard {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1e3a8a;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setContentsMargins(12, 6, 12, 12)
        self.scroll_layout.setSpacing(12)
        self.scroll.setWidget(self.container)

        self.refresh(self.prompts)

    def refresh(self, prompts):
        self.clear()
        self.prompts = prompts or []
    
        if not self.prompts:
            return  # << GEEN tijdelijke QLabel toevoegen
    
        for index, prompt in enumerate(self.prompts):
            card = PromptCard(index, prompt, self)
            card.clicked.connect(lambda idx=index: self.prompt_selected.emit(idx))
            card.toggled_favorite.connect(lambda idx=index: self.toggled_favorite.emit(idx))
            self.scroll_layout.addWidget(card)
    
        self.scroll_layout.addStretch()


    def clear(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)


    def load_prompts(self, prompts):
        self.refresh(prompts)

    def select_first(self):
        if self.prompts:
            self.prompt_selected.emit(0)
