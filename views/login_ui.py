from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from controllers.auth_controller import AuthController

class LoginWindow(QWidget):
    def __init__(self, main_app_callback):
        super().__init__()
        self.main_app_callback = main_app_callback
        self.controller = AuthController()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Acceso - Supermercado JPV")
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #2c3e50;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Contenedor Blanco
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 10px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # Título
        title = QLabel("INICIAR SESIÓN")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; border: none;")
        
        # Inputs
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario (ej: Juancito)")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Botón
        btn_login = QPushButton("Ingresar")
        btn_login.clicked.connect(self.handle_login)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 12px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addWidget(btn_login)

        layout.addWidget(card)
        self.setLayout(layout)

    def handle_login(self):
        user = self.user_input.text()
        pwd = self.pass_input.text()
        
        user_data = self.controller.login(user, pwd)
        
        if user_data:
            # Login exitoso
            self.close()
            # Callback para abrir la ventana principal, pasamos el ID y ROL
            self.main_app_callback(user_data) 
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")