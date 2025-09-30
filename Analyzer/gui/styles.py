"""
Modern styling module for Dispute Analysis Tool
Provides consistent styling across the application
"""

class Colors:
    """Color palette for the application"""
    # Primary colors
    PRIMARY = "#3c6e71"
    PRIMARY_DARK = "#284b63"
    PRIMARY_LIGHT = "#4a7c81"
    
    # Secondary colors
    SECONDARY = "#d9d9d9"
    SECONDARY_DARK = "#b5b5b5"
    SECONDARY_LIGHT = "#f5f5f5"
    
    # Accent colors
    ACCENT = "#ff7f50"  # Coral
    ACCENT_DARK = "#e56a46"
    ACCENT_LIGHT = "#ff9a7b"
    
    # Status colors
    SUCCESS = "#28a745"
    WARNING = "#ffc107"
    ERROR = "#dc3545"
    INFO = "#17a2b8"
    
    # Neutrals
    WHITE = "#ffffff"
    BLACK = "#000000"
    GRAY_DARK = "#343a40"
    GRAY_MEDIUM = "#6c757d"
    GRAY_LIGHT = "#ced4da"
    
    # Special colors
    GOLD = "#ffd700"
    SILVER = "#c0c0c0"


class Typography:
    """Typography settings for the application"""
    FONT_FAMILY = "Segoe UI, Helvetica, Arial, sans-serif"
    FONT_FAMILY_MONO = "Consolas, Monaco, 'Courier New', monospace"
    
    # Font sizes (px)
    FONT_SIZE_XXS = 10
    FONT_SIZE_XS = 12
    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 16
    FONT_SIZE_LARGE = 18
    FONT_SIZE_XL = 24
    FONT_SIZE_XXL = 32
    
    # Font weights
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_BOLD = 700
    
    # Line heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_LOOSE = 1.8


class Layout:
    """Layout measurements and constants"""
    # Padding and margins
    PADDING_XXS = 2
    PADDING_XS = 4
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24
    PADDING_XL = 32
    PADDING_XXL = 48
    
    # Border radius
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_LARGE = 16
    
    # Shadows
    SHADOW_SMALL = "0 2px 4px rgba(0, 0, 0, 0.1)"
    SHADOW_MEDIUM = "0 4px 8px rgba(0, 0, 0, 0.12)"
    SHADOW_LARGE = "0 8px 16px rgba(0, 0, 0, 0.15)"
    
    # Button dimensions
    BUTTON_HEIGHT = 36
    BUTTON_WIDTH_SMALL = 80
    BUTTON_WIDTH_MEDIUM = 120
    BUTTON_WIDTH_LARGE = 180
    
    # Table dimensions
    TABLE_ROW_HEIGHT = 36
    TABLE_HEADER_HEIGHT = 48


def get_modern_style():
    """
    Returns the complete stylesheet for the application
    """
    return f"""
        /* Global styles */
        QWidget {{
            font-family: {Typography.FONT_FAMILY};
            font-size: {Typography.FONT_SIZE_MEDIUM}px;
            color: {Colors.GRAY_DARK};
            background-color: {Colors.SECONDARY_LIGHT};
        }}
        
        /* Card container */
        QFrame#card {{
            background-color: {Colors.WHITE};
            border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
            border: 1px solid {Colors.GRAY_LIGHT};
        }}
        
        /* Headers */
        QLabel#title {{
            font-size: {Typography.FONT_SIZE_XXL}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {Colors.PRIMARY_DARK};
            padding: {Layout.PADDING_MEDIUM}px;
        }}
        
        QLabel#subtitle {{
            font-size: {Typography.FONT_SIZE_LARGE}px;
            color: {Colors.GRAY_MEDIUM};
            margin-bottom: {Layout.PADDING_LARGE}px;
        }}
        
        QLabel#filterLabel {{
            font-size: {Typography.FONT_SIZE_MEDIUM}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {Colors.PRIMARY};
            margin-top: {Layout.PADDING_MEDIUM}px;
        }}
        
        /* Status labels */
        QLabel#statusLabel {{
            font-size: {Typography.FONT_SIZE_MEDIUM}px;
            color: {Colors.INFO};
            font-style: italic;
        }}
        
        QLabel#varLabel {{
            font-size: {Typography.FONT_SIZE_LARGE}px;
            font-weight: {Typography.WEIGHT_BOLD};
        }}
        
        /* Buttons */
        QPushButton {{
            height: {Layout.BUTTON_HEIGHT}px;
            border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            padding: 0 {Layout.PADDING_MEDIUM}px;
        }}
        
        QPushButton#primaryButton {{
            background-color: {Colors.PRIMARY};
            color: {Colors.WHITE};
            border: none;
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: {Colors.PRIMARY_DARK};
        }}
        
        QPushButton#primaryButton:pressed {{
            background-color: {Colors.PRIMARY_DARK};
        }}
        
        QPushButton#secondaryButton {{
            background-color: {Colors.SECONDARY};
            color: {Colors.GRAY_DARK};
            border: 1px solid {Colors.GRAY_LIGHT};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {Colors.SECONDARY_DARK};
        }}
        
        QPushButton#accentButton {{
            background-color: {Colors.ACCENT};
            color: {Colors.WHITE};
            border: none;
        }}
        
        QPushButton#accentButton:hover {{
            background-color: {Colors.ACCENT_DARK};
        }}
        
        /* Combo boxes */
        QComboBox {{
            border: 1px solid {Colors.GRAY_LIGHT};
            border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            padding: {Layout.PADDING_SMALL}px;
            background-color: {Colors.WHITE};
            selection-background-color: {Colors.PRIMARY_LIGHT};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        /* Tables */
        QTableWidget {{
            border: 1px solid {Colors.GRAY_LIGHT};
            border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            gridline-color: {Colors.GRAY_LIGHT};
            selection-background-color: {Colors.PRIMARY_LIGHT};
            selection-color: {Colors.WHITE};
        }}
        
        QTableWidget::item {{
            padding: {Layout.PADDING_SMALL}px;
            border-bottom: 1px solid {Colors.GRAY_LIGHT};
        }}
        
        QHeaderView::section {{
            background-color: {Colors.PRIMARY};
            color: {Colors.WHITE};
            padding: {Layout.PADDING_SMALL}px;
            border: none;
            font-weight: {Typography.WEIGHT_BOLD};
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            border: 1px solid {Colors.GRAY_LIGHT};
            border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {Colors.SECONDARY};
            color: {Colors.GRAY_DARK};
            padding: {Layout.PADDING_SMALL}px {Layout.PADDING_MEDIUM}px;
            margin-right: 2px;
            border-top-left-radius: {Layout.BORDER_RADIUS_SMALL}px;
            border-top-right-radius: {Layout.BORDER_RADIUS_SMALL}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {Colors.PRIMARY};
            color: {Colors.WHITE};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            spacing: {Layout.PADDING_MEDIUM}px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {Colors.GRAY_MEDIUM};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {Colors.PRIMARY};
            border-color: {Colors.PRIMARY};
        }}
        
        /* Radio buttons */
        QRadioButton {{
            spacing: {Layout.PADDING_MEDIUM}px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {Colors.GRAY_MEDIUM};
            border-radius: 9px;
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {Colors.PRIMARY};
            border-color: {Colors.PRIMARY};
        }}
        
        /* Dialog boxes */
        QDialog {{
            background-color: {Colors.SECONDARY_LIGHT};
        }}
        
        /* Text browsers */
        QTextBrowser {{
            border: 1px solid {Colors.GRAY_LIGHT};
            border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            background-color: {Colors.WHITE};
            padding: {Layout.PADDING_MEDIUM}px;
        }}
    """
