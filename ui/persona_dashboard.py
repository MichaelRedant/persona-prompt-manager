# ui/persona_dashboard.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from ui.persona_card import PersonaCard


class PersonaDashboard(QWidget):
    persona_selected = Signal(int)
    favorite_toggled = Signal(int)

    def __init__(self, parent=None, personas=None):
        super().__init__(parent)
        self.personas = personas or []

        self.setObjectName("personaDashboard")
        self.setStyleSheet("""
            QWidget#personaDashboard {
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

        self.title = QLabel("📊 Persona Dashboard")
        layout.addWidget(self.title)

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

        self.refresh(self.personas)

    def refresh(self, personas):
        # Oude widgets verwijderen
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.personas = personas or []

        if not self.personas:
            empty_label = QLabel("Geen persona's beschikbaar.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for index, persona in enumerate(self.personas):
            card = PersonaCard(index, persona)
            card.setCursor(Qt.PointingHandCursor)
            card.clicked.connect(lambda checked=False, i=index: self.persona_selected.emit(i))

            card.toggled_favorite.connect(self.favorite_toggled.emit)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()
