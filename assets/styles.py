APP_STYLE = """
    /* GLOBAL SETTINGS - LIGHT THEME */
    QWidget {
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 14px;
        color: #000000;
        background-color: #ffffff;
    }
    
    QMainWindow, QWidget#MainContent {
        background-color: #f8f9fa;
    }
    
    /* SIDEBAR (Classic Blue ERP Style) */
    QFrame#Sidebar {
        background-color: #004085;
        border-right: 2px solid #002752;
    }
    QLabel#SidebarTitle {
        color: #ffffff;
        font-size: 22px;
        font-weight: bold;
        padding: 20px;
        background-color: #002752;
    }
    
    /* SIDEBAR BUTTONS */
    QPushButton.SidebarBtn {
        background-color: transparent;
        color: #ffffff;
        text-align: left;
        padding: 15px 20px;
        border: none;
        font-size: 16px;
        border-bottom: 1px solid #0056b3;
    }
    QPushButton.SidebarBtn:hover {
        background-color: #0056b3;
        font-weight: bold;
        padding-left: 25px;
    }
    QPushButton.SidebarBtn:checked {
        background-color: #ffc107; /* Active Yellow */
        color: #000000;
        font-weight: bold;
    }

    /* CARDS & PANELS */
    QFrame, QGroupBox {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }
    QLabel {
        color: #212529;
    }
    QLabel.Header {
        font-size: 24px;
        font-weight: bold;
        color: #004085;
        margin-bottom: 15px;
    }
    
    /* INPUTS */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        background-color: #ffffff;
        border: 2px solid #ced4da;
        border-radius: 4px;
        padding: 8px;
        color: #000000;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #007bff;
        background-color: #f0f8ff;
    }
    
    /* BUTTONS */
    QPushButton {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QPushButton#successBtn {
        background-color: #28a745;
    }
    QPushButton#dangerBtn {
        background-color: #dc3545;
    }
    
    /* TABLES */
    QTableWidget {
        background-color: #ffffff;
        gridline-color: #dee2e6;
        color: #000000;
        selection-background-color: #007bff;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background-color: #343a40;
        color: #ffffff;
        padding: 8px;
        font-weight: bold;
    }
"""
