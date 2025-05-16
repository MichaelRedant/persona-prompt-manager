from PySide6.QtWidgets import QSplashScreen, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap, QFont, QPainter
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QByteArray, QEasingCurve, QRect
import os

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Correct pad naar startup.png
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "assets", "startup.png")

        # Fallback naar blanco indien geen image
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print("⚠️ Splash image niet gevonden:", image_path)
            pixmap = QPixmap(800, 400)
            pixmap.fill(Qt.black)

        super().__init__(pixmap)

        # Zorg dat splash altijd bovenaan is
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Fade-in effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(1200)  # in ms
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # Styling
        self.setFont(QFont("Segoe UI", 12))
        self.showMessage(
            "🧠 Persona Vault wordt geladen...\n👤 door Michaël Redant",
            Qt.AlignBottom | Qt.AlignCenter,
            Qt.white
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()
