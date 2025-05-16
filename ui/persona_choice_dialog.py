from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class PersonaChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧠 Nieuwe Persona Aanmaken")
        self.setFixedSize(480, 220)
        self.setStyleSheet("""
            QLabel {
                font-size: 17px;
                font-weight: 600;
                padding-bottom: 12px;
                color: #1e293b;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                font-size: 16px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)

        layout = QVBoxLayout()
        label = QLabel("Welke soort persona wil je aanmaken?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        self.blank_button = QPushButton("📝 Blanco Persona")
        self.template_button = QPushButton("🎯 Persona via Template")

        button_layout.addStretch()
        button_layout.addWidget(self.blank_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.template_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.blank_button.clicked.connect(lambda: self.done(1))
        self.template_button.clicked.connect(lambda: self.done(2))
