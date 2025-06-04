from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QSpacerItem, QSizePolicy
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
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(12)
        self.scroll.setWidget(self.container)
        self.scroll.setMaximumHeight(400)

        self.no_personas_label = QLabel("Geen persona's gevonden.")
        self.no_personas_label.setAlignment(Qt.AlignCenter)
        self.no_personas_label.setStyleSheet("color: #777; font-style: italic;")
        self.no_personas_label.setVisible(False)
        self.scroll_layout.addWidget(self.no_personas_label)

        self.refresh(self.personas)

    def refresh(self, personas):
        self.clear_personas()
        self.personas = personas or []

        if not self.personas:
            self.no_personas_label.setVisible(True)
            return
        else:
            self.no_personas_label.setVisible(False)

        for index, persona in enumerate(self.personas):
            card = PersonaCard(index, persona)
            card.setCursor(Qt.PointingHandCursor)

            # Emit de index naar buiten bij klik op de kaart
            card.clicked.connect(lambda checked=False, i=index: self.persona_selected.emit(i))

            # Favoriet toggle en ster visueel updaten
            card.toggled_favorite.connect(lambda i=index, c=card: self._handle_favorite_toggle(i, c))

            card.update_ui()
            self.scroll_layout.addWidget(card)

        # Enkel als er effectief iets werd toegevoegd
        if self.scroll_layout.count() > 1:
            spacer = QSpacerItem(0, 24, QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.scroll_layout.addItem(spacer)

    def _handle_favorite_toggle(self, index, card):
        self.favorite_toggled.emit(index)  # Laat main logic dit opslaan
        card.persona.is_favorite = not card.persona.is_favorite  # Toggle lokale status
        card.update_ui()  # Ster bijwerken

    def clear_personas(self):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            widget = item.widget()
            if widget and widget != self.no_personas_label:
                widget.setParent(None)
                widget.deleteLater()
            elif not widget:
                self.scroll_layout.removeItem(item)
