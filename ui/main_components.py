from PySide6.QtWidgets import (
    QVBoxLayout, QScrollArea, QWidget, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QFrame, QSizePolicy, QLineEdit, QListWidget, QGraphicsDropShadowEffect
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui.tag_filter_panel import TagFilterPanel
from ui.persona_dashboard import PersonaDashboard
from logic.ai_mood import determine_ai_mood
from ui.main_events import show_mood_insights
from ui.main_events import filter_by_tag
from ui.main_events import open_prompt_wizard
from ui.main_events import try_prompt_in_chatgpt

def build_components(main):
    
# 📦 Hoofdlayout eerst definiëren
    layout = QVBoxLayout()
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(20)
    # 🧠 Titel
    title_label = QLabel("🧠 Persona Vault")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("""
        font-size: 36px;
        font-weight: 800;
        color: #1e3a8a;
        padding: 32px;
        border-radius: 16px;
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #e0e7ff,
            stop:1 #c7d2fe
        );
    """)
    # Mood ophalen op basis van persona’s
    main.current_mood = determine_ai_mood([])  # leeg bij init
    main.status_chip = QLabel()
    main.status_chip.setAlignment(Qt.AlignRight)
    main.status_chip.setStyleSheet(main.get_chip_style())
    main.status_chip.mousePressEvent = lambda event: show_mood_insights(main, event)
    main.status_chip.setCursor(Qt.PointingHandCursor)
    # 👋 Subtitel
    subtitle = QLabel("Welkom terug, Michaël — klaar om een nieuwe prompt te bouwen?")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setStyleSheet("font-size: 14px; color: #64748b; margin-top: 0px; margin-bottom: 16px;")
    # 🧭 Header Layout
    header_layout = QVBoxLayout()
    header_layout.addWidget(main.status_chip, alignment=Qt.AlignRight)
    header_layout.addWidget(title_label)
    header_layout.addWidget(subtitle)
    # 📌 Voeg header toe aan layout
    layout.addLayout(header_layout)


    
     # Zoekfunctie
    main.search_toggle_button = QPushButton("🔍")
    main.search_toggle_button.setFixedWidth(120)
    main.search_toggle_button.setStyleSheet("""
        QPushButton {
            background-color: #4f46e5;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #4338ca;
        }
    """)
    main.search_input = QLineEdit()
    main.search_input.setPlaceholderText("Typ om te zoeken...")
    main.search_input.hide()
    main.search_input.setFixedWidth(300)
    main.search_input.setStyleSheet("""
        QLineEdit {
            background-color: white;
            padding: 10px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #4f46e5;
            outline: none;
        }
    """)

    search_row = QHBoxLayout()
    search_row.setSpacing(12)
    search_row.addWidget(main.search_toggle_button)
    search_row.addWidget(main.search_input)

 
    # Prompt UI
    main.prompt_list = QListWidget()
    main.no_prompts_label = QLabel("Geen prompts gevonden.")
    main.no_prompts_label.setAlignment(Qt.AlignCenter)
    main.no_prompts_label.hide()
    prompt_card_widget = wrap_in_card(main, main.prompt_list, "💡 Prompts")
    prompt_wrapper = QVBoxLayout()
    prompt_wrapper.addWidget(main.no_prompts_label)
    prompt_wrapper.addWidget(prompt_card_widget)
    prompt_card_container = QFrame()
    prompt_card_container.setLayout(prompt_wrapper)

    from ui.tag_filter_panel import TagFilterPanel
    main.filter_by_tag = filter_by_tag.__get__(main)
    main.tag_panel = TagFilterPanel(main)


    top_layout = QHBoxLayout()
    top_layout.setSpacing(12)
     
    # Persona UI
    main.persona_dashboard = PersonaDashboard(main)
    top_layout.addWidget(main.persona_dashboard, 4)
    
    top_layout.addWidget(prompt_card_container, 3)
    top_layout.addWidget(main.tag_panel, 2)

    # Prompttekst
    main.prompt_details_box = QTextEdit()
    main.prompt_details_box.setReadOnly(True)
    main.prompt_details_box.setMinimumHeight(200)
    prompt_card = wrap_in_card(main, main.prompt_details_box, "✏️ Prompttekst")
    
    # Interactieknoppen
    main.copy_prompt_button = QPushButton("📋 Kopieer prompt")
    main.copy_prompt_button.clicked.connect(main.copy_prompt)
    main.copy_prompt_button.setCursor(Qt.PointingHandCursor)
    main.copy_prompt_button.setStyleSheet("""
        QPushButton {
            background-color: #4f46e5;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #4338ca;
        }
    """)
    
    
    
    main.prompt_info_label = QLabel()
    main.prompt_info_label.setStyleSheet("font-size: 12px; color: #6b7280;")
    main.prompt_info_label.setWordWrap(True)
    main.prompt_tip_label = QLabel("💡 Tip: Start prompts met een duidelijke rol, zoals \"Je bent een expert copywriter...\"")
    main.prompt_tip_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
    main.prompt_tip_label.setWordWrap(True)
    main.try_prompt_button = QPushButton("🧪 Test prompt in ChatGPT")
    main.try_prompt_button.clicked.connect(lambda: try_prompt_in_chatgpt(main))
    main.try_prompt_button.setCursor(Qt.PointingHandCursor)
    main.try_prompt_button.setStyleSheet("""
        QPushButton {
            background-color: #16a34a;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #15803d;
        }
    """)
    # ➕ Genereer Prompt-knop
    main.generate_prompt_button = QPushButton("🎛️ Genereer Prompt")
    main.generate_prompt_button.clicked.connect(lambda: open_prompt_wizard(main))
    main.generate_prompt_button.setCursor(Qt.PointingHandCursor)
    main.generate_prompt_button.setStyleSheet("""
        QPushButton {
            background-color: #0ea5e9;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #0284c7;
        }
    """)
    test_button_box = QVBoxLayout()
    test_button_box.setSpacing(10)
    test_button_box.addWidget(main.copy_prompt_button)
    test_button_box.addWidget(main.prompt_info_label)
    test_button_box.addWidget(main.prompt_tip_label)
    # ➕ Voeg Genereer Prompt-knop toe vóór de Test-knop
    test_button_box.addWidget(main.generate_prompt_button)
    test_button_box.addWidget(main.try_prompt_button)
    test_button_box.addStretch()

    test_card = QFrame()
    test_card.setLayout(test_button_box)
    test_card.setStyleSheet("background-color: transparent;")

    prompt_row = QHBoxLayout()
    prompt_row.setSpacing(20)
    prompt_row.addWidget(prompt_card, 5)
    prompt_row.addWidget(test_card, 3)

    # Beschrijving
    main.details_box = QTextEdit()
    main.details_box.setReadOnly(True)
    main.details_box.setMinimumHeight(100)

    main.prompt_metadata_label = QLabel()
    main.prompt_metadata_label.setStyleSheet("font-size: 12px; color: #6b7280; padding-left: 12px; padding-top: 4px;")

    main.add_persona_button = QPushButton("➕ Nieuwe Persona")

    main.edit_persona_button = QPushButton("✏️ Bewerken Persona")
    main.edit_persona_button.hide()
    
    main.delete_persona_button = QPushButton("❌ Verwijderen Persona")
    main.delete_persona_button.hide()
    
    main.favorite_button = QPushButton("⭐ Toggle Favoriet")
    main.favorite_button.hide()


    persona_btns = QHBoxLayout()
    persona_btns.addWidget(main.add_persona_button)
    persona_btns.addWidget(main.edit_persona_button)
    persona_btns.addWidget(main.delete_persona_button)
    persona_btns.addWidget(main.favorite_button)

    main.add_prompt_button = QPushButton("➕ Nieuwe Prompt")
    main.edit_prompt_button = QPushButton("✏️ Bewerken Prompt")
    main.delete_prompt_button = QPushButton("❌ Verwijderen Prompt")

    prompt_btns = QHBoxLayout()
    prompt_btns.addWidget(main.add_prompt_button)
    prompt_btns.addWidget(main.edit_prompt_button)
    prompt_btns.addWidget(main.delete_prompt_button)
       
    
    # Layout opbouw
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(20)
    layout.addLayout(search_row)
    layout.addLayout(top_layout)
    layout.addLayout(prompt_row)
    layout.addWidget(wrap_in_card(main, main.details_box, "🧠 Beschrijving"))
    layout.addWidget(main.prompt_metadata_label)
    layout.addLayout(persona_btns)
    layout.addLayout(prompt_btns)

    container_widget = QWidget()
    container_widget.setLayout(layout)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(container_widget)
    main.setCentralWidget(scroll_area)

    return layout, scroll_area

def wrap_in_card(main, widget: QWidget, title: str = None) -> QFrame:
    frame = QFrame()
    layout = QVBoxLayout(frame)

    if title:
        title_label = QLabel(title)
        title_label.setStyleSheet("""
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
        """)
        layout.addWidget(title_label)

    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout.addWidget(widget)

    # Kleur & stijl
    bg_color = '#2d2d2d' if getattr(main, 'is_dark_mode', False) else 'white'
    text_color = '#e0e0e0' if getattr(main, 'is_dark_mode', False) else '#1e293b'
    border_color = '#444' if getattr(main, 'is_dark_mode', False) else '#e5e7eb'

    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: 12px;
            border: 1px solid {border_color};
            padding: 12px;
        }}
    """)

    # Schaduw
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(12)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 50))
    frame.setGraphicsEffect(shadow)

    return frame

