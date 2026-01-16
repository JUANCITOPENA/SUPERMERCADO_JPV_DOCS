import sys
from PyQt6.QtWidgets import QApplication
from views.login_ui import LoginWindow
from views.main_window_ui import MainWindow
import qdarktheme

def open_main_window(user_data):
    # Esta función se llama cuando el login es exitoso
    global window
    window = MainWindow(user_data)
    window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- CORRECCIÓN COMPATIBILIDAD PYTHON 3.13 ---
    try:
        # Intenta cargar el tema con el método moderno (v2.x)
        qdarktheme.setup_theme("auto")
    except AttributeError:
        # Si da error (como en tu caso con v0.1.7), usa el método antiguo
        print("⚠️ Usando modo compatibilidad (Legacy Theme)")
        app.setStyleSheet(qdarktheme.load_stylesheet())
    # ---------------------------------------------

    # Iniciar con Login
    login = LoginWindow(open_main_window)
    login.show()
    
    sys.exit(app.exec())