from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from assets.styles import APP_STYLE
try:
    import qtawesome as qta
except ImportError:
    qta = None

from views.dashboard_ui import DashboardWindow
from views.pos_ui import POSWindow
from views.inventory_ui import InventoryWindow
from views.clients_ui import ClientsWindow
from views.reports_ui import ReportsWindow

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"ERP Supermercado JPV - {self.user_data[1].upper()}")
        self.resize(1280, 800)
        self.setStyleSheet(APP_STYLE)

        # Main Layout (Horizontal: Sidebar | Content)
        central_widget = QWidget()
        central_widget.setObjectName("MainContent")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo / Title
        app_title = QLabel("SUPERMERCADO\nJPV")
        app_title.setObjectName("SidebarTitle")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Navigation Buttons
        self.btn_dashboard = self.create_nav_btn("Dashboard", "fa.dashboard", 0)
        self.btn_pos = self.create_nav_btn("Punto de Venta", "fa.shopping-cart", 1)
        self.btn_inventory = self.create_nav_btn("Inventario", "fa.cubes", 2)
        self.btn_clients = self.create_nav_btn("Clientes", "fa.users", 3)
        self.btn_reports = self.create_nav_btn("Reportes", "fa.file-pdf-o", 4)
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_pos)
        sidebar_layout.addWidget(self.btn_inventory)
        sidebar_layout.addWidget(self.btn_clients)
        sidebar_layout.addWidget(self.btn_reports)
        
        sidebar_layout.addStretch() 
        
        # User Info
        user_info = QLabel(f"👤 {self.user_data[0]}")
        user_info.setStyleSheet("color: #bdc3c7; padding: 20px; font-weight: bold;")
        sidebar_layout.addWidget(user_info)

        btn_exit = QPushButton("Cerrar Sesión")
        btn_exit.setStyleSheet("background-color: #c0392b; color: white; border: none; padding: 15px;")
        btn_exit.clicked.connect(self.close)
        sidebar_layout.addWidget(btn_exit)

        # --- Content Area ---
        self.stack = QStackedWidget()
        
        # Initialize Views
        self.view_dashboard = DashboardWindow()
        self.view_pos = POSWindow(self.user_data)
        self.view_inventory = InventoryWindow()
        self.view_clients = ClientsWindow()
        self.view_reports = ReportsWindow()

        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_pos)
        self.stack.addWidget(self.view_inventory)
        self.stack.addWidget(self.view_clients)
        self.stack.addWidget(self.view_reports)

        # Add to Main Layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Set Dashboard as default
        self.btn_dashboard.click()

    def create_nav_btn(self, text, icon_name, index):
        btn = QPushButton(f"  {text}")
        btn.setProperty("class", "SidebarBtn")
        btn.setCheckable(True)
        if qta:
            btn.setIcon(qta.icon(icon_name, color="#bdc3c7"))
        
        btn.clicked.connect(lambda: self.switch_page(index, btn))
        return btn

    def switch_page(self, index, btn_sender):
        self.stack.setCurrentIndex(index)
        
        # Reset styles
        for btn in [self.btn_dashboard, self.btn_pos, self.btn_inventory, self.btn_clients, self.btn_reports]:
            btn.setChecked(False)
        
        btn_sender.setChecked(True)
