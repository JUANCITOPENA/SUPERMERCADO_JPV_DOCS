
from PyQt6.QtWidgets import *
from assets.styles import APP_STYLE
from views.inventory_ui import InventoryWindow
from views.pos_ui import POSWindow
from views.dashboard_ui import DashboardWindow
from views.clients_ui import ClientsWindow
from views.vendors_ui import VendorsWindow
from views.reports_ui import ReportsWindow

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__(); self.user_data = user_data; self.init_ui()
    def init_ui(self):
        self.setWindowTitle(f"SUPERMERCADO JPV V9 - {self.user_data[1].upper()}"); self.resize(1200, 800); self.setStyleSheet(APP_STYLE)
        cw = QWidget(); self.setCentralWidget(cw); main = QHBoxLayout(cw); main.setContentsMargins(0,0,0,0)
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(250); main.addWidget(side); s_lay = QVBoxLayout(side)
        lbl = QLabel("MENU PRINCIPAL"); lbl.setObjectName("SidebarTitle"); s_lay.addWidget(lbl)
        self.stack = QStackedWidget(); main.addWidget(self.stack)
        
        pages = [("📊 Dashboard", DashboardWindow()), ("🛒 POS", POSWindow(self.user_data)), ("📦 Inventario", InventoryWindow()), 
                 ("👥 Clientes", ClientsWindow()), ("👔 Vendedores", VendorsWindow()), ("📄 Reportes", ReportsWindow())]
        for i, (txt, win) in enumerate(pages):
            btn = QPushButton(txt); btn.setProperty("class", "SidebarBtn"); btn.clicked.connect(lambda _, x=i: self.stack.setCurrentIndex(x))
            s_lay.addWidget(btn); self.stack.addWidget(win)
        s_lay.addStretch(); btn_out = QPushButton("🚪 SALIR"); btn_out.clicked.connect(self.close); s_lay.addWidget(btn_out)
