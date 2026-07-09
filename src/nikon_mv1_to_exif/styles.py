"""Dark theme stylesheet for the application."""

DARK_STYLESHEET = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "SF Pro Text", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1e1e2e;
}

QDialog {
    background-color: #1e1e2e;
}

QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 8px;
    background-color: #181825;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px 14px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #45475a;
    color: #89b4fa;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: 600;
    color: #cba6f7;
}

QLabel#subtitleLabel {
    color: #a6adc8;
    font-size: 12px;
}

QGroupBox {
    border: 1px solid #313244;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #89b4fa;
}

QLineEdit, QTextEdit, QTableWidget {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #585b70;
}

QLineEdit:focus, QTextEdit:focus, QTableWidget:focus {
    border: 1px solid #89b4fa;
}

QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #b4befe;
}

QPushButton#primaryButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton:disabled {
    color: #6c7086;
}

QTableWidget {
    gridline-color: #313244;
    alternate-background-color: #181825;
}

QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QProgressBar {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 8px;
    text-align: center;
    color: #cdd6f4;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 7px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #45475a;
    background-color: #181825;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QScrollBar:vertical {
    background: #181825;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
