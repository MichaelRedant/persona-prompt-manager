from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import QEasingCurve, QPropertyAnimation


def apply_button_effects(button, base_color: str, hover_color: str):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(16)
    shadow.setXOffset(0)
    shadow.setYOffset(3)
    shadow.setColor(QColor(0, 0, 0, 80))
    button.setGraphicsEffect(shadow)

    anim = QPropertyAnimation(button, b"styleSheet")
    anim.setDuration(250)
    anim.setEasingCurve(QEasingCurve.OutCubic)

    normal_style = f"""
        QPushButton {{
            background-color: {base_color};
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """
    button.setStyleSheet(normal_style)
