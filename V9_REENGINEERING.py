import os
import pyodbc

# CONFIGURACION DB
DB_CONFIG = {
    'server': r'(localdb)\MSSQLLocalDB',
    'database': 'SUPERMERCADO_JPV_V6',
    'conn_str': f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=(localdb)\\MSSQLLocalDB;DATABASE=SUPERMERCADO_JPV_V6;Trusted_Connection=yes;"
}

# --- 1. ASSETS: STYLES (LUMINOUS HIGH CONTRAST) ---
code_styles = """
APP_STYLE = \"\"\"
    QWidget { font-family: 'Segoe UI'; font-size: 14px; color: #000000; background-color: #ffffff; }
    QMainWindow { background-color: #f0f2f5; }
    QFrame#Sidebar { background-color: #003366; border-right: 2px solid #002244; }
    QLabel#SidebarTitle { color: #ffffff; font-size: 20px; font-weight: bold; padding: 20px; background-color: #002244; }
    QPushButton.SidebarBtn { 
        background-color: transparent; color: #ffffff; text-align: left; padding: 15px; border: none; 
        border-bottom: 1px solid #004488; font-size: 15px;
    }
    QPushButton.SidebarBtn:hover { background-color: #0055aa; }
    QPushButton.SidebarBtn:checked { background-color: #ffcc00; color: #000000; font-weight: bold; }
    
    QGroupBox { font-weight: bold; border: 2px solid #003366; border-radius: 8px; margin-top: 10px; padding-top: 10px; }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { 
        border: 2px solid #ced4da; border-radius: 4px; padding: 8px; color: #000000; background-color: #ffffff;
    }
    QLineEdit:focus { border: 2px solid #007bff; background-color: #f0f8ff; }
    
    QPushButton { background-color: #007bff; color: white; border-radius: 5px; padding: 10px; font-weight: bold; }
    QPushButton:hover { background-color: #0056b3; }
    QPushButton#successBtn { background-color: #28a745; }
    QPushButton#dangerBtn { background-color: #dc3545; }
    
    QTableWidget { background-color: #ffffff; gridline-color: #dee2e6; color: #000000; selection-background-color: #007bff; }
    QHeaderView::section { background-color: #003366; color: #ffffff; padding: 8px; font-weight: bold; border: 1px solid #ffffff; }
\"\"\"
"""

# --- 2. UTILS: HELPERS ---
code_helpers = """
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import requests
from database import db

def load_img(url, size=(150, 150)):
    pix = QPixmap(size[0], size[1])
    pix.fill(Qt.GlobalColor.lightGray)
    if not url or 'http' not in url: return pix
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            img = QImage()
            img.loadFromData(resp.content)
            pix = QPixmap.fromImage(img)
    except: pass
    return pix.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

def get_next_id(table, col):
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT ISNULL(MAX({col}), 0) + 1 FROM {table}")
    res = cursor.fetchone()[0]
    conn.close()
    return res
"""

# --- 3. CONTROLLERS ---
code_controllers = {
    "auth_controller.py": """
from database import db
class AuthController:
    def login(self, user, pwd):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_USUARIO, ROL FROM USUARIOS WHERE NOMBRE_USUARIO=? AND PASSWORD=HASHBYTES('SHA2_256', CAST(? AS VARCHAR(50)))", (user, pwd))
        res = cursor.fetchone()
        conn.close()
        return res
""",
    "products_controller.py": """
from database import db
class ProductController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT P.ID_PRODUCTO, P.PRODUCTO, P.STOCK, P.PRECIO_VENTA, ISNULL(FP.foto_Productos_url, '') FROM PRODUCTO P LEFT JOIN FOTO_PRODUCTOS FP ON P.ID_PRODUCTO=FP.ID_PRODUCTO"
        if search: sql += f" WHERE P.PRODUCTO LIKE '%{search}%' OR CAST(P.ID_PRODUCTO AS VARCHAR) LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res
    def save(self, id_p, nom, stock, pc, pv, url):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("IF EXISTS(SELECT 1 FROM PRODUCTO WHERE ID_PRODUCTO=?) UPDATE PRODUCTO SET PRODUCTO=?, STOCK=?, PRECIO_COMPRA=?, PRECIO_VENTA=? WHERE ID_PRODUCTO=? ELSE INSERT INTO PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA) VALUES (?,?,?,?,?)", (id_p, nom, stock, pc, pv, id_p, id_p, nom, stock, pc, pv))
            cursor.execute("DELETE FROM FOTO_PRODUCTOS WHERE ID_PRODUCTO=?", (id_p,))
            if url: cursor.execute("INSERT INTO FOTO_PRODUCTOS (ID_Foto, foto_Productos_url, ID_PRODUCTO) VALUES (?,?,?)", (id_p+7000, url, id_p))
            conn.commit()
            return True, "Guardado"
        except Exception as e: return False, str(e)
        finally: conn.close()
""",
    "client_controller.py": """
from database import db
class ClientController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, RNC_CEDULA, TIPO_PERSONA FROM CLIENTE"
        if search: sql += f" WHERE NOMBRE_CLIENTE LIKE '%{search}%' OR RNC_CEDULA LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res
    def get_geo(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_REGION, REGION FROM REGION")
        regs = cursor.fetchall()
        cursor.execute("SELECT id_provincia, nombreProvincia, id_region FROM PROVINCIAS")
        provs = cursor.fetchall()
        conn.close()
        return regs, provs
""",
    "sales_controller.py": """
from database import db
class SalesController:
    def get_clients(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_CLIENTE, NOMBRE_CLIENTE + ' ' + APELLIDO_CLIENTE, RNC_CEDULA FROM CLIENTE").fetchall()
        conn.close()
        return res
    def get_products(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_PRODUCTO, PRODUCTO, PRECIO_VENTA, STOCK FROM PRODUCTO").fetchall()
        conn.close()
        return res
    def process_sale(self, cid, vid, pid, qty, pay, deli):
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("EXEC SP_FACTURAR_VENTA ?, ?, ?, ?, ?, ?", (cid, vid, pid, qty, pay, deli))
            conn.commit()
            return True, "Venta Procesada con NCF"
        except Exception as e: return False, str(e).split(']')[-1]
        finally: conn.close()
"""
}

# --- 4. VIEWS ---
code_views = {
    "inventory_ui.py": """
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from controllers.products_controller import ProductController
from utils.helpers import load_img, get_next_id

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl = ProductController()
        self.init_ui()
        self.load_data()
    def init_ui(self):
        layout = QHBoxLayout(self)
        left = QVBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍 Filtrar Productos..."); self.search.textChanged.connect(self.load_data)
        left.addWidget(self.search)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["ID", "Producto", "Stock", "Precio"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill)
        left.addWidget(self.table)
        
        right = QGroupBox("Formulario de Producto")
        form = QFormLayout(right)
        self.img_lbl = QLabel(); self.img_lbl.setFixedSize(150,150); self.img_lbl.setStyleSheet("border:1px solid #ccc")
        form.addRow(self.img_lbl)
        self.inp_id = QSpinBox(); self.inp_id.setRange(1,999999)
        self.inp_nom = QLineEdit()
        self.inp_stk = QSpinBox(); self.inp_stk.setRange(-100,9999)
        self.inp_pc = QDoubleSpinBox(); self.inp_pc.setMaximum(99999)
        self.inp_pv = QDoubleSpinBox(); self.inp_pv.setMaximum(99999)
        self.inp_url = QLineEdit(); self.inp_url.textChanged.connect(lambda: self.img_lbl.setPixmap(load_img(self.inp_url.text())))
        form.addRow("ID:", self.inp_id); form.addRow("Nombre:", self.inp_nom); form.addRow("Stock:", self.inp_stk)
        form.addRow("Costo:", self.inp_pc); form.addRow("Venta:", self.inp_pv); form.addRow("URL Foto:", self.inp_url)
        btn_save = QPushButton("💾 GUARDAR PRODUCTO"); btn_save.setObjectName("successBtn"); btn_save.clicked.connect(self.save)
        btn_new = QPushButton("✨ NUEVO"); btn_new.clicked.connect(self.clear)
        form.addRow(btn_save); form.addRow(btn_new)
        
        layout.addLayout(left, 2); layout.addWidget(right, 1)
    def load_data(self):
        data = self.ctrl.get_all(self.search.text())
        self.table.setRowCount(0)
        for i, r in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i,0,QTableWidgetItem(str(r[0])))
            self.table.setItem(i,1,QTableWidgetItem(r[1]))
            item = QTableWidgetItem(str(r[2]))
            if r[2]<=5: item.setBackground(Qt.GlobalColor.red); item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(i,2,item)
            self.table.setItem(i,3,QTableWidgetItem(f"{r[3]:.2f}"))
    def fill(self, item):
        row = self.ctrl.get_all(self.table.item(item.row(), 0).text())[0]
        self.inp_id.setValue(row[0]); self.inp_nom.setText(row[1]); self.inp_stk.setValue(row[2]); self.inp_pv.setValue(float(row[3])); self.inp_url.setText(row[4])
    def clear(self):
        self.inp_id.setValue(get_next_id('PRODUCTO', 'ID_PRODUCTO')); self.inp_nom.clear(); self.inp_stk.setValue(0); self.inp_url.clear()
    def save(self):
        ok, m = self.ctrl.save(self.inp_id.value(), self.inp_nom.text(), self.inp_stk.value(), self.inp_pc.value(), self.inp_pv.value(), self.inp_url.text())
        if ok: QMessageBox.information(self, "Exito", m); self.load_data()
        else: QMessageBox.warning(self, "Error", m)
""",
    "pos_ui.py": """
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from controllers.sales_controller import SalesController

class POSWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.uid = user_data[0]; self.ctrl = SalesController()
        self.init_ui(); self.load_masters()
    def init_ui(self):
        layout = QHBoxLayout(self)
        left = QGroupBox("Panel de Facturacion")
        form = QFormLayout(left)
        self.cb_cli = QComboBox(); self.cb_cli.setEditable(True)
        self.cb_pro = QComboBox(); self.cb_pro.setEditable(True); self.cb_pro.currentIndexChanged.connect(self.upd_info)
        self.lbl_info = QLabel("Stock: - | Precio: -"); self.lbl_info.setStyleSheet("font-weight:bold; color:blue")
        self.sp_qty = QSpinBox(); self.sp_qty.setRange(1,1000); self.sp_qty.valueChanged.connect(self.upd_total)
        self.lbl_total = QLabel("RD$ 0.00"); self.lbl_total.setStyleSheet("font-size:30px; color:green; font-weight:bold")
        form.addRow("Cliente:", self.cb_cli); form.addRow("Producto:", self.cb_pro); form.addRow(self.lbl_info)
        form.addRow("Cantidad:", self.sp_qty); form.addRow("TOTAL:", self.lbl_total)
        btn = QPushButton("🚀 PROCESAR FACTURA (F5)"); btn.setMinimumHeight(60); btn.setObjectName("successBtn"); btn.clicked.connect(self.sell)
        form.addRow(btn)
        layout.addWidget(left, 1)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["Producto", "Cant", "Precio", "Subtotal"])
        layout.addWidget(self.table, 2)
    def load_masters(self):
        self.cb_cli.clear(); [self.cb_cli.addItem(f"{c[1]} ({c[2]})", c[0]) for c in self.ctrl.get_clients()]
        self.cb_pro.clear(); self.pm = {p[0]: p for p in self.ctrl.get_products()}
        [self.cb_pro.addItem(p[1], p[0]) for p in self.pm.values()]
    def upd_info(self):
        pid = self.cb_pro.currentData()
        if pid in self.pm: p = self.pm[pid]; self.lbl_info.setText(f"Stock: {p[3]} | Precio: RD$ {p[2]:.2f}"); self.upd_total()
    def upd_total(self):
        pid = self.cb_pro.currentData()
        if pid in self.pm: self.lbl_total.setText(f"RD$ {float(self.pm[pid][2])*self.sp_qty.value()*1.18:,.2f}")
    def sell(self):
        ok, m = self.ctrl.process_sale(self.cb_cli.currentData(), self.uid, self.cb_pro.currentData(), self.sp_qty.value(), 1, 1)
        if ok: QMessageBox.information(self, "Venta", m); self.load_masters()
        else: QMessageBox.critical(self, "Error", m)
"""
}

# --- EJECUCION ---
print("🔥 INICIANDO REINGENIERIA V9...")

# Escribir Assets y Utils
with open("assets/styles.py", "w", encoding="utf-8") as f: f.write(code_styles)
with open("utils/helpers.py", "w", encoding="utf-8") as f: f.write(code_helpers)

# Escribir Controladores
for name, content in code_controllers.items():
    with open(f"controllers/{name}", "w", encoding="utf-8") as f: f.write(content)

# Escribir Vistas
for name, content in code_views.items():
    with open(f"views/{name}", "w", encoding="utf-8") as f: f.write(content)

# Corregir Main Window para incluir todo
code_main = """
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
"""
with open("views/main_window_ui.py", "w", encoding="utf-8") as f: f.write(code_main)

print("✅ REINGENIERIA COMPLETADA. EJECUTE python main.py")
