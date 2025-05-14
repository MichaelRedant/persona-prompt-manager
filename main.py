from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("""
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
    }

    QMainWindow {
        background-color: #f4f6f9;
    }

    QListWidget, QTextEdit {
        background-color: white;
        padding: 10px;
        border: 1px solid #d1d5db;
        border-radius: 10px;
    }

    QLabel {
        font-weight: 600;
        font-size: 15px;
        color: #374151;
    }

    QPushButton {
        background-color: #4f46e5;
        color: white;
        padding: 10px 18px;
        font-size: 15px;
        font-weight: 600;
        border-radius: 8px;
        border: none;
    }

    QPushButton:hover {
        background-color: #4338ca;
    }

    QPushButton:disabled {
        background-color: #d1d5db;
        color: #6b7280;
    }

    QListWidget::item:selected {
        background-color: #e0e7ff;
        color: #1e3a8a;
    }

    QTextEdit {
        line-height: 1.5em;
    }
""")


    window = MainWindow()
    window.show()
    app.exec()
