from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from ui.prompt_card import PromptCard
from models.prompt import Prompt

class PromptDashboard(QWidget):
    prompt_selected = Signal(int)

    def __init__(self, parent=None, prompts=None):
        super().__init__(parent)
        self.prompts = prompts or []
        self._selected_index = -1

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
        # Vorige widgets verwijderen
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.prompts = prompts or []

        if not self.prompts:
            empty_label = QLabel("Geen prompts beschikbaar.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for index, prompt in enumerate(self.prompts):
            card = PromptCard(index, prompt, parent=self.container)
            card.setCursor(Qt.PointingHandCursor)

            card.clicked.connect(lambda _, i=index: self.prompt_selected.emit(i))

            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def get_selected_index(self):
        return self._selected_index

    def clear(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def load_prompts(self, prompts):
        self.refresh(prompts)

    def select_first(self):
        if self.prompts:
            self._selected_index = 0
            self.prompt_selected.emit(0)
