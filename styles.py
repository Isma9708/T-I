"""
Qt Styles Module - Adapts design system for PyQt applications
"""

class Colors:
    DARK_BLUE = "#071d56"
    MEDIUM_BLUE = "#6fadea"
    GOLD = "#dfb950"
    BEIGE = "#e3d7c2"
    CREMA = "#f6f3ef"
    LIGHT_BLUE = "#c4e6fc"
    WHITE = "#ffffff"
    GRAY_DARK = "#58595B"
    GRAY_MEDIUM = "#e1e8ed"
    GRAY_LIGHT = "#f3f6fa"
    BLACK = "#000000"
    
    # Additional derived colors for UI elements
    BUTTON_HOVER = "#0a2a7a"  # Slightly lighter than dark blue
    BUTTON_ACTIVE = "#050f2d"  # Slightly darker than dark blue
    DISABLED = "#cccccc"
    ERROR = "#e74c3c"
    SUCCESS = "#2ecc71"
    WARNING = "#f39c12"
    
    # Background gradient definitions - for future advanced styling
    GRADIENT_BLUE = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {DARK_BLUE}, stop:1 {MEDIUM_BLUE})"
    GRADIENT_GOLD = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {GOLD}, stop:1 {BEIGE})"

class Typography:
    FONT_FAMILY_PRIMARY = "Segoe UI"
    FONT_FAMILY_SECONDARY = "Arial"
    FONT_FAMILY_MONOSPACE = "Consolas"
    
    # Font sizes
    FONT_SIZE_XS = 8
    FONT_SIZE_SMALL = 10
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_XXL = 24
    FONT_SIZE_XXXL = 32
    
    # Font weights
    FONT_WEIGHT_LIGHT = "light"
    FONT_WEIGHT_NORMAL = "normal"
    FONT_WEIGHT_BOLD = "bold"

class Layout:
    PADDING_XS = 4
    PADDING_SMALL = 8
    PADDING_MEDIUM = 12
    PADDING_LARGE = 16
    PADDING_XL = 24
    PADDING_XXL = 30
    
    MARGIN_XS = 4
    MARGIN_SMALL = 8
    MARGIN_MEDIUM = 12
    MARGIN_LARGE = 16
    MARGIN_XL = 24
    
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_LARGE = 16
    BORDER_RADIUS_XL = 24
    
    # Standard widths for controls
    BUTTON_WIDTH_SMALL = 80
    BUTTON_WIDTH_MEDIUM = 120
    BUTTON_WIDTH_LARGE = 200
    
    # Standard heights
    CONTROL_HEIGHT_SMALL = 24
    CONTROL_HEIGHT_MEDIUM = 32
    CONTROL_HEIGHT_LARGE = 40

def get_modern_style():
    """
    Returns a complete QSS stylesheet for the modern professional UI
    """
    return f"""
    /* Main Application */
    QMainWindow {{ 
        background: {Colors.CREMA}; 
    }}
    
    /* Card Widget */
    #card {{ 
        background: {Colors.WHITE}; 
        border-radius: {Layout.BORDER_RADIUS_XL}px; 
        border: 1px solid {Colors.GRAY_MEDIUM};
    }}
    
    /* Labels */
    QLabel {{ 
        color: {Colors.DARK_BLUE}; 
    }}
    
    QLabel#title {{
        color: {Colors.DARK_BLUE};
        font-size: {Typography.FONT_SIZE_XXXL}px;
        font-weight: bold;
    }}
    
    QLabel#subtitle {{
        color: {Colors.GRAY_DARK};
        font-size: {Typography.FONT_SIZE_XL}px;
    }}
    
    QLabel#filterLabel {{
        color: {Colors.DARK_BLUE};
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        font-weight: bold;
    }}
    
    QLabel#statusLabel {{
        color: {Colors.GRAY_DARK};
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
    }}
    
    QLabel#varLabel {{
        color: {Colors.GOLD};
        font-size: {Typography.FONT_SIZE_LARGE}px;
        font-weight: bold;
    }}
    
    /* ComboBoxes */
    QComboBox {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.GRAY_MEDIUM};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        padding: {Layout.PADDING_MEDIUM}px;
        min-height: {Layout.CONTROL_HEIGHT_MEDIUM}px;
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        selection-background-color: {Colors.LIGHT_BLUE};
        selection-color: {Colors.DARK_BLUE};
    }}
    
    QComboBox:hover {{
        border: 1px solid {Colors.MEDIUM_BLUE};
    }}
    
    QComboBox:focus {{
        border: 2px solid {Colors.MEDIUM_BLUE};
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left-width: 0px;
        border-top-right-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        border-bottom-right-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
    }}
    
    /* Buttons */
    QPushButton#primaryButton {{
        background-color: {Colors.DARK_BLUE};
        color: {Colors.WHITE};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        padding: {Layout.PADDING_MEDIUM}px {Layout.PADDING_XL}px;
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        font-weight: bold;
        min-height: {Layout.CONTROL_HEIGHT_MEDIUM}px;
    }}
    
    QPushButton#primaryButton:hover {{
        background-color: {Colors.BUTTON_HOVER};
    }}
    
    QPushButton#primaryButton:pressed {{
        background-color: {Colors.BUTTON_ACTIVE};
    }}
    
    QPushButton#secondaryButton {{
        background-color: {Colors.MEDIUM_BLUE};
        color: {Colors.WHITE};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        padding: {Layout.PADDING_MEDIUM}px {Layout.PADDING_XL}px;
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        min-height: {Layout.CONTROL_HEIGHT_MEDIUM}px;
    }}
    
    QPushButton#secondaryButton:hover {{
        background-color: {Colors.DARK_BLUE};
    }}
    
    QPushButton#secondaryButton:pressed {{
        background-color: {Colors.BUTTON_ACTIVE};
    }}
    
    QPushButton#accentButton {{
        background-color: {Colors.GOLD};
        color: {Colors.DARK_BLUE};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        padding: {Layout.PADDING_MEDIUM}px {Layout.PADDING_XL}px;
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        font-weight: bold;
        min-height: {Layout.CONTROL_HEIGHT_MEDIUM}px;
    }}
    
    QPushButton#accentButton:hover {{
        background-color: {Colors.BEIGE};
    }}
    
    /* Table Widget */
    QTableWidget {{
        background-color: {Colors.WHITE};
        alternate-background-color: {Colors.CREMA};
        border: 1px solid {Colors.GRAY_MEDIUM};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        gridline-color: {Colors.GRAY_MEDIUM};
        selection-background-color: {Colors.LIGHT_BLUE};
        selection-color: {Colors.DARK_BLUE};
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
    }}
    
    QTableWidget::item {{
        padding: {Layout.PADDING_SMALL}px;
    }}
    
    QHeaderView::section {{
        background-color: {Colors.DARK_BLUE};
        color: {Colors.WHITE};
        padding: {Layout.PADDING_MEDIUM}px;
        border: none;
        font-weight: bold;
    }}
    
    QHeaderView::section:first {{
        border-top-left-radius: {Layout.BORDER_RADIUS_SMALL}px;
    }}
    
    QHeaderView::section:last {{
        border-top-right-radius: {Layout.BORDER_RADIUS_SMALL}px;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {Colors.GRAY_LIGHT};
        width: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {Colors.MEDIUM_BLUE};
        min-height: 30px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {Colors.DARK_BLUE};
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background: {Colors.GRAY_LIGHT};
        height: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {Colors.MEDIUM_BLUE};
        min-width: 30px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {Colors.DARK_BLUE};
    }}
    
    /* Remove scrollbar buttons */
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
        border: none;
    }}
    
    /* Message box styling */
    QMessageBox {{
        background-color: {Colors.WHITE};
    }}
    
    QMessageBox QPushButton {{
        background-color: {Colors.DARK_BLUE};
        color: {Colors.WHITE};
        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
        padding: {Layout.PADDING_MEDIUM}px {Layout.PADDING_XL}px;
        font-size: {Typography.FONT_SIZE_MEDIUM}px;
        min-width: {Layout.BUTTON_WIDTH_MEDIUM}px;
        min-height: {Layout.CONTROL_HEIGHT_MEDIUM}px;
    }}
    
    QMessageBox QPushButton:hover {{
        background-color: {Colors.BUTTON_HOVER};
    }}
    """