# assets/styles.py
APP_STYLE = """
    /* DISEÑO LUMINOSO DE ALTO CONTRASTE */
    QWidget {
        font-family: 'Segoe UI', Arial;
        font-size: 14px;
        color: #000000; /* Negro puro para texto */
        background-color: #FFFFFF; /* Blanco puro para fondo */
    }
    
    QMainWindow, QStackedWidget {
        background-color: #F0F2F5;
    }

    /* SIDEBAR AZUL PROFUNDO */
    QFrame#Sidebar {
        background-color: #002D62;
        border-right: 2px solid #001A35;
    }
    
    QLabel#SidebarTitle {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: bold;
        padding: 20px;
        background-color: #001A35;
    }

    QPushButton.SidebarBtn {
        background-color: transparent;
        color: #E0E0E0;
        text-align: left;
        padding: 15px 20px;
        border: none;
        border-bottom: 1px solid #003D82;
        font-weight: 500;
    }
    
    QPushButton.SidebarBtn:hover {
        background-color: #004A99;
        color: #FFFFFF;
    }
    
    QPushButton.SidebarBtn:checked {
        background-color: #FFD700; /* Oro para resaltar selección */
        color: #000000;
        font-weight: bold;
    }

    /* FORMULARIOS Y GRIDS */
    QGroupBox {
        font-weight: bold;
        border: 2px solid #002D62;
        border-radius: 10px;
        margin-top: 15px;
        padding: 15px;
        background-color: #FFFFFF;
    }

    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        border: 2px solid #ADB5BD;
        border-radius: 5px;
        padding: 10px;
        color: #000000;
        background-color: #FFFFFF;
    }

    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #007BFF;
        background-color: #F8FBFF;
    }

    /* BOTONES ACCIÓN */
    QPushButton {
        background-color: #007BFF; /* Azul Vibrante */
        color: #FFFFFF;
        border-radius: 6px;
        padding: 12px;
        font-weight: bold;
    }

    QPushButton:hover { background-color: #0056B3; }
    
    QPushButton#successBtn { background-color: #28A745; } /* Verde Éxito */
    QPushButton#successBtn:hover { background-color: #218838; }
    
    QPushButton#dangerBtn { background-color: #DC3545; } /* Rojo Alerta */
    QPushButton#dangerBtn:hover { background-color: #C82333; }

    /* TABLAS */
    QTableWidget {
        background-color: #FFFFFF;
        gridline-color: #DEE2E6;
        selection-background-color: #CCE5FF;
        selection-color: #000000;
        border: 1px solid #DEE2E6;
    }

    QHeaderView::section {
        background-color: #002D62;
        color: #FFFFFF;
        padding: 10px;
        font-weight: bold;
        border: 1px solid #FFFFFF;
    }
"""
