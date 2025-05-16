from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from collections import defaultdict

class TagFilterPanel(QGroupBox):
    def __init__(self, parent=None, tag_clicked_callback=None):
        super(TagFilterPanel, self).__init__("📑 Tags", parent)

        self.setStyleSheet("""
    QGroupBox {
        font-size: 15px;
        font-weight: bold;
        padding: 8px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background-color: transparent;
    }
    QPushButton {
        background-color: #e0e7ff;
        color: #1e3a8a;
        border: none;
        border-radius: 6px;
        padding: 6px 10px;
        margin: 3px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #dbeafe;
    }
    QPushButton[selected="true"] {
        background-color: #4338ca;
        color: white;
        font-weight: bold;
    }
""")


        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(160)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.tag_clicked_callback = tag_clicked_callback

        self.active_tag = None
        self.tag_buttons = {}

        # 🔁 Resetknop
        self.reset_button = QPushButton("🔁 Toon alles")
        self.reset_button.clicked.connect(self.clear_filter)
        self.layout.addWidget(self.reset_button)

    def update_tags(self, personas, prompts):
        self.clear_tags(keep_reset=True)

        tag_count = defaultdict(int)
        for p in personas:
            for tag in p.tags:
                tag_count[tag] += 1
        for p in prompts:
            for tag in p.tags:
                tag_count[tag] += 1

        sorted_tags = sorted(tag_count.items(), key=lambda x: (-x[1], x[0].lower()))

        for tag, count in sorted_tags:
            label = f"{tag} ({count})"
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("selected", str(tag == self.active_tag).lower())
            btn.clicked.connect(lambda _, t=tag: self.handle_tag_click(t))
            self.layout.addWidget(btn)
            self.tag_buttons[tag] = btn

        self.layout.addStretch()

    def clear_tags(self, keep_reset=False):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget and (not keep_reset or widget != self.reset_button):
                widget.setParent(None)
        if keep_reset:
            self.tag_buttons.clear()
        else:
            self.active_tag = None
            self.tag_buttons.clear()

    def handle_tag_click(self, tag):
        if self.active_tag == tag:
            self.clear_filter()
        else:
            self.active_tag = tag
            if self.tag_clicked_callback:
                self.tag_clicked_callback(tag)
            self.refresh_selection_state()

    def clear_filter(self):
        self.active_tag = None
        if self.tag_clicked_callback:
            self.tag_clicked_callback(None)
        self.refresh_selection_state()

    def refresh_selection_state(self):
        for tag, btn in self.tag_buttons.items():
            btn.setProperty("selected", str(tag == self.active_tag).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)
