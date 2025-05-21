# ui/prompt_wizard.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QTabWidget, QWidget, QApplication, QHBoxLayout
)
from PySide6.QtCore import Qt


class WizardTab(QWidget):
    def __init__(self, title, questions, parent_wizard, index):
        super().__init__()
        self.parent_wizard = parent_wizard
        self.index = index

        layout = QVBoxLayout(self)
        title_label = QLabel(f"🧩 {title}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; margin-bottom: 4px;")
        layout.addWidget(title_label)

        # Helpvragen als label erboven
        if questions:
            help_text = "\n".join(f"• {q}" for q in questions)
            help_label = QLabel(help_text)
            help_label.setStyleSheet("font-size: 13px; color: #64748b; margin-bottom: 6px;")
            help_label.setWordWrap(True)
            layout.addWidget(help_label)

        self.text = QTextEdit()
        self.text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #1e293b;
            }
        """)
        layout.addWidget(self.text)

        # Navigatieknoppen onderaan
        btns = QHBoxLayout()
        if index > 0:
            prev_btn = QPushButton("⬅️ Vorige")
            prev_btn.clicked.connect(self.go_prev)
            btns.addWidget(prev_btn)
        btns.addStretch()
        next_btn = QPushButton("➡️ Volgende")
        next_btn.clicked.connect(self.go_next)
        btns.addWidget(next_btn)
        layout.addLayout(btns)

    def go_next(self):
        if self.index + 1 < self.parent_wizard.tabs.count():
            self.parent_wizard.tabs.setCurrentIndex(self.index + 1)
        else:
            self.parent_wizard.generate()

    def go_prev(self):
        if self.index - 1 >= 0:
            self.parent_wizard.tabs.setCurrentIndex(self.index - 1)


class PromptWizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧠 Persona Prompt Wizard")
        self.setMinimumSize(900, 700)
        self.sections = {}
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QTabWidget::pane { border: none; margin: 0; }
            QTextEdit, QLabel { font-family: 'Segoe UI', sans-serif; }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)

        self.step_indicator = QLabel()
        self.step_indicator.setAlignment(Qt.AlignCenter)
        self.step_indicator.setStyleSheet("font-size: 16px; color: #334155; padding: 8px;")
        
        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()  # verberg standaard tab bar
        self.tabs.currentChanged.connect(self.update_step_indicator)

        self.section_definitions = self.define_sections()
        for i, section in enumerate(self.section_definitions):
            tab = WizardTab(section['title'], section['questions'], self, i)
            self.sections[section['title']] = tab.text
            self.tabs.addTab(tab, section['title'])

        self.generate_btn = QPushButton("✨ Genereer Prompt")
        self.generate_btn.clicked.connect(self.generate)

        layout = QVBoxLayout()
        layout.addWidget(self.step_indicator)
        layout.addWidget(self.tabs)
        layout.addWidget(self.generate_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

        self.update_step_indicator(0)

    def update_step_indicator(self, index):
        total = self.tabs.count()
        circles = ["🔵" if i == index else "⚪" for i in range(total)]
        self.step_indicator.setText(" ".join(circles) + f"   —   Sectie {index+1} van {total}")

    def define_sections(self):
        return [
            {"title": "Algemene Beschrijving", "questions": [
                "Wat is de functietitel van deze persona?",
                "Wat is hun expertisegebied of specialisatie?",
                "Wat maakt deze persoon uniek in zijn/haar vakgebied?"
            ]},
            {"title": "Belangrijkste Taken", "questions": [
                "Welke dagelijkse taken voert deze persona uit?",
                "Welke workflows of processen zijn kenmerkend?",
                "Waar ligt hun verantwoordelijkheid in een team?"
            ]},
            {"title": "Sectorgerichte Toepassingen", "questions": [
                "In welke sector(en) is deze persona actief?",
                "Welke unieke toepassingen gebruikt hij/zij in deze sector?",
                "Voor welk soort projecten wordt deze persona typisch ingezet?"
            ]},
            {"title": "Jargon & Technieken", "questions": [
                "Welke vaktermen of jargon gebruikt deze persona?",
                "Welke technieken of methodologieën worden gehanteerd?",
                "Zijn er typische frameworks of tools verbonden aan deze functie?"
            ]},
            {"title": "Gedragskenmerken", "questions": [
                "Welke karaktereigenschappen typeren deze persona?",
                "Hoe gedraagt hij/zij zich in teamverband?",
                "Wat is hun houding tegenover problemen en innovatie?"
            ]},
            {"title": "Doelen & Succescriteria", "questions": [
                "Wat wil deze persona bereiken in zijn/haar rol?",
                "Wanneer is deze persona succesvol volgens zichzelf of het team?",
                "Welke KPI's of doelstellingen worden opgevolgd?"
            ]},
            {"title": "Samenwerking", "questions": [
                "Met welke andere rollen werkt deze persona vaak samen?",
                "Wat is de aard van die samenwerking?",
                "Hoe wordt kennis of informatie gedeeld?"
            ]},
            {"title": "Tools & Software", "questions": [
                "Welke tools of platformen gebruikt deze persona dagelijks?",
                "Zijn er specifieke softwarepakketten essentieel in deze rol?",
                "Welke technische skills zijn vereist?"
            ]},
            {"title": "Uitdagingen & Oplossingen", "questions": [
                "Welke terugkerende uitdagingen ervaart deze persona?",
                "Hoe worden deze meestal opgelost?",
                "Zijn er creatieve workaround-oplossingen?"
            ]},
            {"title": "GPT-Stijl", "questions": [
                "Wat is de gewenste communicatiestijl van deze persona?",
                "Moet de output meer adviserend, technisch of creatief zijn?",
                "Wil je formele of informele output van GPT?"
            ]},
            {"title": "Structuur & Visualisatie", "questions": [
                "Wens je tabellen, schema’s of grafieken in de output?",
                "Welke visuele elementen moet GPT gebruiken?",
                "Moet de output een vaste structuur volgen?"
            ]},
            {"title": "Vermijdingspunten", "questions": [
                "Wat moet GPT vermijden in de antwoorden?",
                "Zijn er woorden, concepten of stijlen die niet passen?",
                "Moet de output steeds voorbeelden bevatten?"
            ]},
            {"title": "Follow-up Vragen", "questions": [
                "Welke verdiepende vragen moet GPT stellen aan de gebruiker?",
                "Wat zijn relevante vervolgstappen na een eerste antwoord?",
                "Hoe kan GPT de context verder verduidelijken?"
            ]}
        ]

    def generate(self):
        result = ""
        for title, input_field in self.sections.items():
            content = input_field.toPlainText().strip()
            if content:
                result += f"### {title}\n\n{content}\n\n"

        dlg = QDialog(self)
        dlg.setWindowTitle("📄 Gegenereerde Prompt")
        dlg.setMinimumSize(700, 500)
        layout = QVBoxLayout(dlg)

        output = QTextEdit()
        output.setReadOnly(True)
        output.setText(result)
        layout.addWidget(output)

        copy_btn = QPushButton("📋 Kopieer naar klembord")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(result))
        layout.addWidget(copy_btn)

        dlg.exec()
