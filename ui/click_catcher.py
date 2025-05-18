from PySide6.QtWidgets import QFrame

class ClickCatcherFrame(QFrame):
    def __init__(self, parent=None, on_click=None):
        super().__init__(parent)
        self.on_click = on_click
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")
        self.setFrameShape(QFrame.NoFrame)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click()
        super().mousePressEvent(event)
