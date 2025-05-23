# ui/persona_card.py

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models.persona import Persona

class PersonaCard(QFrame):
    clicked = Signal(int)
    toggled_favorite = Signal(int)

    def __init__(self, index: int, persona: Persona):
        super().__init__()
        self.index = index
        self.persona = persona

        self.setObjectName("personaCard")
        self.setStyleSheet("""
            QFrame#personaCard {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background-color: white;
            }
            QLabel {
                font-size: 13px;
                color: #1f2937;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name_label = QLabel(f"{persona.name}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        category_label = QLabel(f"🧩 {persona.category}")
        tags_label = QLabel("🏷️ " + ", ".join(persona.tags) if persona.tags else "")

        text_layout.addWidget(name_label)
        text_layout.addWidget(category_label)
        text_layout.addWidget(tags_label)

        layout.addLayout(text_layout)

        self.favorite_btn = QPushButton("⭐" if persona.is_favorite else "☆")
        self.favorite_btn.setFixedWidth(24)
        self.favorite_btn.setCursor(Qt.PointingHandCursor)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        layout.addWidget(self.favorite_btn, alignment=Qt.AlignRight)

    def mousePressEvent(self, event):
       self.clicked.emit(self.index)
       event.accept()  # voorkomt verder bubbling naar bovenliggende handlers


    def toggle_favorite(self):
        self.toggled_favorite.emit(self.index)
