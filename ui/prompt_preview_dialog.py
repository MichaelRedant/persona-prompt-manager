from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QApplication
from PySide6.QtCore import Qt

class PromptPreviewDialog(QDialog):
    def __init__(self, persona_name: str, prompt_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎛️ Preview gegenereerde prompt")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        title = QLabel(f"🎛️ Prompt voor: {persona_name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(title)

        self.preview_box = QTextEdit()
        self.preview_box.setReadOnly(True)
        self.preview_box.setPlainText(prompt_text)
        self.preview_box.setStyleSheet("background: white; font-size: 13px;")
        layout.addWidget(self.preview_box)

        button_row = QHBoxLayout()
        self.copy_btn = QPushButton("📋 Kopieer prompt")
        self.close_btn = QPushButton("Sluiten")

        button_row.addWidget(self.copy_btn)
        button_row.addStretch()
        button_row.addWidget(self.close_btn)
        layout.addLayout(button_row)

        # Events
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.close_btn.clicked.connect(self.close)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_box.toPlainText())
