#!/usr/bin/env python3
"""
Estilos y Temas de la Aplicación
===============================

Este módulo contiene todos los estilos CSS y configuraciones de tema
para la aplicación de predicción de hormigón.
"""

# Colores principales del tema
COLORS = {
    'primary': '#2563eb',
    'primary_dark': '#1d4ed8',
    'primary_light': '#3b82f6',
    'secondary': '#64748b',
    'success': '#059669',
    'warning': '#d97706',
    'danger': '#dc2626',
    'background': '#f8fafc',
    'surface': '#ffffff',
    'surface_alt': '#f1f5f9',
    'text_primary': '#1e293b',
    'text_secondary': '#64748b',
    'text_muted': '#94a3b8',
    'border': '#e2e8f0',
    'border_focus': '#2563eb'
}

def get_main_window_style() -> str:
    """Estilo principal para la ventana principal."""
    return f"""
    QMainWindow {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
    }}
    
    QWidget {{
        background-color: transparent;
        color: {COLORS['text_primary']};
    }}
    
    /* Menú */
    QMenuBar {{
        background-color: {COLORS['surface']};
        border-bottom: 1px solid {COLORS['border']};
        padding: 4px 0px;
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: 6px 12px;
        margin: 0px 2px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['primary_light']};
        color: white;
    }}
    
    QMenu {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 8px 16px;
        margin: 2px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['primary_light']};
        color: white;
    }}
    
    /* Barra de estado */
    QStatusBar {{
        background-color: {COLORS['surface']};
        border-top: 1px solid {COLORS['border']};
        padding: 4px 8px;
    }}
    
    QStatusBar::item {{
        border: none;
        padding: 0px 4px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['border']};
        width: 2px;
        height: 2px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['primary']};
    }}
    """

def get_group_box_style() -> str:
    """Estilo para QGroupBox."""
    return f"""
    QGroupBox {{
        font-size: 12pt;
        font-weight: bold;
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: {COLORS['surface']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        top: -8px;
        background-color: {COLORS['surface']};
        padding: 0 8px;
        color: {COLORS['primary']};
    }}
    """

def get_button_style() -> str:
    """Estilo para botones."""
    return f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 11pt;
        font-weight: 500;
        min-width: 100px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['primary_dark']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['primary_dark']};
        transform: translateY(1px);
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['text_muted']};
        color: {COLORS['surface_alt']};
    }}
    
    /* Botón secundario */
    QPushButton[buttonType="secondary"] {{
        background-color: {COLORS['surface_alt']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
    }}
    
    QPushButton[buttonType="secondary"]:hover {{
        background-color: {COLORS['border']};
        border-color: {COLORS['text_secondary']};
    }}
    
    /* Botón de éxito */
    QPushButton[buttonType="success"] {{
        background-color: {COLORS['success']};
    }}
    
    QPushButton[buttonType="success"]:hover {{
        background-color: #047857;
    }}
    
    /* Botón de advertencia */
    QPushButton[buttonType="warning"] {{
        background-color: {COLORS['warning']};
    }}
    
    QPushButton[buttonType="warning"]:hover {{
        background-color: #b45309;
    }}
    
    /* Botón de peligro */
    QPushButton[buttonType="danger"] {{
        background-color: {COLORS['danger']};
    }}
    
    QPushButton[buttonType="danger"]:hover {{
        background-color: #b91c1c;
    }}
    """

def get_input_style() -> str:
    """Estilo para campos de entrada."""
    return f"""
    QLineEdit {{
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11pt;
        background-color: {COLORS['surface']};
        selection-background-color: {COLORS['primary_light']};
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['border_focus']};
        background-color: {COLORS['surface']};
    }}
    
    QLineEdit:disabled {{
        background-color: {COLORS['surface_alt']};
        color: {COLORS['text_muted']};
        border-color: {COLORS['surface_alt']};
    }}
    
    /* ComboBox */
    QComboBox {{
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11pt;
        background-color: {COLORS['surface']};
        min-width: 120px;
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['border_focus']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 6px solid {COLORS['text_secondary']};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
        selection-background-color: {COLORS['primary_light']};
        selection-color: white;
        padding: 4px;
    }}
    """

def get_table_style() -> str:
    """Estilo para tablas."""
    return f"""
    QTableWidget {{
        gridline-color: {COLORS['border']};
        background-color: {COLORS['surface']};
        alternate-background-color: {COLORS['surface_alt']};
        selection-background-color: {COLORS['primary_light']};
        selection-color: white;
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['primary_light']};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['surface_alt']};
        color: {COLORS['text_primary']};
        font-weight: bold;
        padding: 10px 8px;
        border: none;
        border-right: 1px solid {COLORS['border']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    QHeaderView::section:first {{
        border-top-left-radius: 6px;
    }}
    
    QHeaderView::section:last {{
        border-top-right-radius: 6px;
        border-right: none;
    }}
    """

def get_tab_style() -> str:
    """Estilo para tabs."""
    return f"""
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
        margin-top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['surface_alt']};
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 10px 16px;
        margin-right: 2px;
        font-weight: 500;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_primary']};
        border-color: {COLORS['border']};
        margin-bottom: -1px;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['border']};
        color: {COLORS['text_primary']};
    }}
    """

def get_scroll_area_style() -> str:
    """Estilo para áreas de desplazamiento."""
    return f"""
    QScrollArea {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
    }}
    
    QScrollBar:vertical {{
        background: {COLORS['surface_alt']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['text_muted']};
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: none;
        border: none;
    }}
    
    QScrollBar:horizontal {{
        background: {COLORS['surface_alt']};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {COLORS['text_muted']};
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        background: none;
        border: none;
    }}
    """

def get_tooltip_style() -> str:
    """Estilo para tooltips."""
    return f"""
    QToolTip {{
        background-color: {COLORS['text_primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 10pt;
        opacity: 230;
    }}
    """

def get_complete_stylesheet() -> str:
    """Obtener hoja de estilos completa."""
    return f"""
    {get_main_window_style()}
    {get_group_box_style()}
    {get_button_style()}
    {get_input_style()}
    {get_table_style()}
    {get_tab_style()}
    {get_scroll_area_style()}
    {get_tooltip_style()}
    
    /* Estilos adicionales específicos */
    QLabel[labelType="title"] {{
        font-size: 18pt;
        font-weight: bold;
        color: {COLORS['text_primary']};
        padding: 8px 0;
    }}
    
    QLabel[labelType="subtitle"] {{
        font-size: 14pt;
        font-weight: 600;
        color: {COLORS['text_secondary']};
        padding: 4px 0;
    }}
    
    QLabel[labelType="caption"] {{
        font-size: 10pt;
        color: {COLORS['text_muted']};
        padding: 2px 0;
    }}
    
    /* Frame para cards */
    QFrame[frameType="card"] {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 16px;
    }}
    
    QFrame[frameType="card"]:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }}
    
    /* Separadores */
    QFrame[frameType="separator"] {{
        background-color: {COLORS['border']};
        border: none;
        max-height: 1px;
        min-height: 1px;
        margin: 8px 0;
    }}
    """

# Configuraciones de fuentes
FONTS = {
    'title': ('Segoe UI', 18, 'bold'),
    'subtitle': ('Segoe UI', 14, 'semibold'),
    'body': ('Segoe UI', 11, 'normal'),
    'caption': ('Segoe UI', 9, 'normal'),
    'monospace': ('Consolas', 10, 'normal')
}