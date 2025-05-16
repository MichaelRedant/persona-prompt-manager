import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen

icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "icon.ico"))

def start_main():
    global window
    window = MainWindow()
    window.show()
    splash.finish(window)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))

    tray_icon = QSystemTrayIcon(QIcon(icon_path))
    tray_icon.setVisible(True)

    splash = SplashScreen()
    splash.show()

    # Geef Qt de tijd om het splash scherm te tonen
    QTimer.singleShot(2500, start_main)

    app.setStyleSheet(""" QWidget { font-family: 'Segoe UI', sans-serif; font-size: 15px; } QMainWindow { background-color: #f4f6f9; } QListWidget, QTextEdit { background-color: white; padding: 10px; border: 1px solid #d1d5db; border-radius: 10px; } QLabel { font-weight: 600; font-size: 15px; color: #374151; } QPushButton { background-color: #4f46e5; color: white; padding: 10px 18px; font-size: 15px; font-weight: 600; border-radius: 8px; border: none; } QPushButton:hover { background-color: #4338ca; } QPushButton:disabled { background-color: #d1d5db; color: #6b7280; } QListWidget::item:selected { background-color: #e0e7ff; color: #1e3a8a; } QTextEdit { line-height: 1.5em; } """)

    app.exec()
