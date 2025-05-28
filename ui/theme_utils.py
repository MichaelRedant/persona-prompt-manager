def toggle_dark_mode(self, enabled):
        self.is_dark_mode = enabled
        self.refresh_persona_list()
        self.rebuild_layout()

        if enabled:
            self.setStyleSheet("""
                * { background-color: #1e1e1e; color: #e0e0e0; }
                QLineEdit, QTextEdit, QListWidget, QMenuBar, QMenu {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #444;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)
        else:
            self.setStyleSheet("")

        self.update()
        
def rebuild_layout(self):
    # Bewaar huidige selectie en zoekterm (optioneel)
        search = self.search_input.text()
        self.search_input.clear()

    # Verwijder en heropbouw layout
        self.centralWidget().deleteLater()
        self.__init__()  # Ja, dit is hier ok: herlaadt alles proper
        self.search_input.setText(search)