# ui/prompt_card.py

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class PromptCard(QFrame):
    clicked = Signal(int)
    toggled_favorite = Signal(int)

    def __init__(self, index: int, prompt, parent=None):
        super().__init__(parent)
        self.index = index
        self.prompt = prompt

        self.setObjectName("promptCard")
        self.setStyleSheet("""
            QFrame#promptCard {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QLabel {
                font-size: 13px;
                color: #1f2937;
            }
            QPushButton {
                border: none;
                background: none;
                font-size: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_layout = QHBoxLayout()
        title_label = QLabel(prompt.title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        favorite_btn = QPushButton("⭐" if prompt.is_favorite else "☆")
        favorite_btn.setCursor(Qt.PointingHandCursor)
        favorite_btn.clicked.connect(lambda: self.toggled_favorite.emit(self.index))

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(favorite_btn)

        layout.addLayout(title_layout)

        if hasattr(prompt, "tags") and prompt.tags:
            tag_text = ", ".join(prompt.tags)
            tag_label = QLabel(f"🏷️ {tag_text}")
            tag_label.setStyleSheet("color: #6b7280; font-size: 11px;")
            layout.addWidget(tag_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
            event.accept()  # voorkom verdere eventbubbling
