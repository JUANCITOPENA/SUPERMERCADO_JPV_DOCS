from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from assets.styles import APP_STYLE
try: import qtawesome as qta
except: qta = None

from views.dashboard_ui import DashboardWindow
from views.pos_ui import POSWindow
from views.inventory_ui import InventoryWindow
from views.clients_ui import ClientsWindow
from views.reports_ui import ReportsWindow
from views.vendors_ui import VendorsWindow

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"ERP Supermercado JPV - {self.user_data[1].upper()}")
        self.resize(1280, 800)
        self.setStyleSheet(APP_STYLE)
        central_widget = QWidget()
        central_widget.setObjectName("MainContent")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        s_layout = QVBoxLayout(self.sidebar)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setSpacing(5)
        title = QLabel("SUPERMERCADO
JPV")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(title)
        self.btns = []
        self.add_menu_btn("Dashboard", "fa5s.tachometer-alt", 0, s_layout)
        self.add_menu_btn("Punto de Venta", "fa5s.shopping-cart", 1, s_layout)
        self.add_menu_btn("Inventario", "fa5s.boxes", 2, s_layout)
        self.add_menu_btn("Clientes", "fa5s.users", 3, s_layout)
        self.add_menu_btn("Vendedores", "fa5s.user-tie", 4, s_layout)
        self.add_menu_btn("Reportes", "fa5s.file-invoice-dollar", 5, s_layout)
        s_layout.addStretch()
        user_info = QLabel(f"Hola, {self.user_data[0]}")
        user_info.setStyleSheet("color: white; padding: 20px; font-weight: bold;")
        s_layout.addWidget(user_info)
        btn_exit = QPushButton("Salir")
        btn_exit.setStyleSheet("background: #c82333; margin: 10px;")
        btn_exit.clicked.connect(self.close)
        s_layout.addWidget(btn_exit)
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardWindow())
        self.stack.addWidget(POSWindow(self.user_data))
        self.stack.addWidget(InventoryWindow())
        self.stack.addWidget(ClientsWindow())
        self.stack.addWidget(VendorsWindow())
        self.stack.addWidget(ReportsWindow())
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

    def add_menu_btn(self, text, icon, idx, layout):
        btn = QPushButton(f"  {text}")
        btn.setProperty("class", "SidebarBtn")
        btn.setCheckable(True)
        if qta: btn.setIcon(qta.icon(icon, color="white"))
        btn.clicked.connect(lambda: self.switch_tab(idx, btn))
        layout.addWidget(btn)
        self.btns.append(btn)
        
    def switch_tab(self, idx, active_btn):
        if idx == 1 and self.user_data[1] != 'admin' and self.user_data[1] != 'vendedor':
             from PyQt6.QtWidgets import QMessageBox
             QMessageBox.warning(self, "Acceso Denegado", "No tienes permisos de Vendedor.")
             return
        self.stack.setCurrentIndex(idx)
        for b in self.btns: b.setChecked(False)
        active_btn.setChecked(True)
