APP_STYLE = """
    /* GLOBAL */
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        color: #333;
    }
    QMainWindow, QWidget#MainContent {
        background-color: #ecf0f1;
    }

    /* SIDEBAR */
    QFrame#Sidebar {
        background-color: #2c3e50;
        border-right: 1px solid #1a252f;
    }
    QLabel#SidebarTitle {
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 20px;
    }
    QPushButton.SidebarBtn {
        background-color: transparent;
        color: #bdc3c7;
        text-align: left;
        padding: 15px 20px;
        border: none;
        font-size: 16px;
    }
    QPushButton.SidebarBtn:hover {
        background-color: #34495e;
        color: white;
        border-left: 4px solid #3498db;
    }
    QPushButton.SidebarBtn:checked {
        background-color: #34495e;
        color: white;
        border-left: 4px solid #1abc9c;
        font-weight: bold;
    }

    /* CARDS */
    QFrame.Card {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    QLabel.CardTitle {
        font-size: 14px;
        color: #7f8c8d;
        font-weight: bold;
    }
    QLabel.CardValue {
        font-size: 28px;
        color: #2c3e50;
        font-weight: bold;
    }
    
    /* FORMS */
    QLineEdit, QComboBox, QSpinBox, QDateEdit {
        background-color: white;
        border: 1px solid #ced4da;
        border-radius: 5px;
        padding: 8px;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #3498db;
    }
    QLabel.FormLabel {
        font-weight: bold;
        color: #34495e;
    }

    /* BUTTONS */
    QPushButton {
        background-color: #2980b9;
        color: white;
        border-radius: 5px;
        padding: 10px 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3498db;
    }
    QPushButton#dangerBtn {
        background-color: #c0392b;
    }
    QPushButton#dangerBtn:hover {
        background-color: #e74c3c;
    }
    QPushButton#successBtn {
        background-color: #27ae60;
    }
    QPushButton#successBtn:hover {
        background-color: #2ecc71;
    }
    QPushButton#warningBtn {
        background-color: #f39c12;
        color: white;
    }

    /* TABLES */
    QTableWidget {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        gridline-color: #ecf0f1;
        selection-background-color: #3498db;
        selection-color: white;
    }
    QHeaderView::section {
        background-color: #34495e;
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
    QTableWidget::item {
        padding: 5px;
    }
"""