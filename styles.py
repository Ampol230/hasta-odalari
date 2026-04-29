"""Hemşire Hasta Takip Sistemi - Stil Tanımları"""

from config import COLORS

MAIN_STYLESHEET = f"""
    QWidget {{
        background-color: {COLORS['bg_dark']}; 
        color: {COLORS['text_main']}; 
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }}
    QPushButton {{
        background-color: #313338;
        border: 1px solid #1e1f22;
        border-radius: 6px;
        padding: 10px 15px;
        font-weight: bold;
        color: {COLORS['text_main']};
    }}
    QPushButton:hover {{
        background-color: #404249;
    }}
    QListWidget {{
        background-color: {COLORS['bg_darker']}; 
        border: none;
        border-radius: 10px;
        padding: 8px;
        outline: none;
    }}
    QListWidget::item {{
        min-height: 45px;
        padding: 8px 12px;
        border-bottom: 1px solid #313338; 
        border-radius: 6px;
        margin-bottom: 3px;
        background-color: #313338;
    }}
    QListWidget::item:hover {{
        background-color: #404249;
        border-left: 3px solid {COLORS['accent']};
        padding-left: 9px;
    }}
    QListWidget::item:selected {{
        background-color: #404249; 
        color: #ffffff;
        font-weight: bold;
        border-left: 4px solid {COLORS['accent']}; 
        padding-left: 8px;
    }}
    QTextEdit {{
        background-color: {COLORS['bg_darker']}; 
        color: {COLORS['text_main']}; 
        border: none;
        border-left: 2px solid rgba(88, 101, 242, 0.3);
        border-radius: 10px;
        padding: 15px;
    }}
    QLineEdit#search_bar {{
        background-color: {COLORS['bg_darker']};
        border: 1px solid {COLORS['bg_darker']};
        border-radius: 10px;
        padding: 12px;
        color: white;
        font-size: 14px;
    }}
    QLineEdit#search_bar:focus {{
        border: 1px solid {COLORS['accent']};
    }}
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['bg_darker']};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: #404249;
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['accent']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

FORM_INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {COLORS['bg_darker']};
        border: 1px solid {COLORS['bg_darker']};
        border-radius: 5px;
        padding: 8px;
        color: white;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {COLORS['accent']};
    }}
    QSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #404249;
        background-color: #313338;
    }}
    QSpinBox::up-button:hover {{
        background-color: {COLORS['accent']};
    }}
    QSpinBox::up-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-bottom: 6px solid {COLORS['text_main']};
        width: 0px;
        height: 0px;
    }}
    QSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border-left: 1px solid #404249;
        background-color: #313338;
    }}
    QSpinBox::down-button:hover {{
        background-color: {COLORS['accent']};
    }}
    QSpinBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS['text_main']};
        width: 0px;
        height: 0px;
    }}
"""

CHECKBOX_STYLE = f"color: {COLORS['text_error']}; font-weight: bold; padding: 2px;"
