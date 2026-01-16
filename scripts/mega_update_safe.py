import os

code_helpers = """from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import requests

def load_image_from_url(url, size=(100, 100)):
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(Qt.GlobalColor.lightGray)
    if not url or url == 'N/A': return pixmap
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap.fromImage(image)
    except: pass
    return pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
"""

code_vendor_controller = """from database import db
import pyodbc

class VendorController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        query = "SELECT V.ID_VENDEDOR, V.VENDEDOR, V.SUCURSAL, P.nombreProvincia, ISNULL(FV.foto_Vendedor_url, '') FROM VENDEDOR V LEFT JOIN PROVINCIAS P ON V.PROVINCIA = P.id_provincia LEFT JOIN FOTOS_VENDEDOR FV ON V.ID_VENDEDOR = FV.ID_vendedor"
        if search: query += f" WHERE V.VENDEDOR LIKE '%{search}%'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

    def get_next_id(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ISNULL(MAX(ID_VENDEDOR), 0) + 1 FROM VENDEDOR")
        next_id = cursor.fetchone()[0]
        conn.close()
        return next_id

    def save(self, id_ven, nombre, sucursal, id_prov, foto_url):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM VENDEDOR WHERE ID_VENDEDOR = ?", (id_ven,))
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute("UPDATE VENDEDOR SET VENDEDOR=?, SUCURSAL=?, PROVINCIA=? WHERE ID_VENDEDOR=?", (nombre, sucursal, id_prov, id_ven))
                cursor.execute("DELETE FROM FOTOS_VENDEDOR WHERE ID_vendedor=?", (id_ven,))
                if foto_url: cursor.execute("INSERT INTO FOTOS_VENDEDOR VALUES (?, ?, ?)", (id_ven + 1000, foto_url, id_ven))
            else:
                cursor.execute("INSERT INTO VENDEDOR (ID_VENDEDOR, VENDEDOR, id_genero, SUCURSAL, PROVINCIA) VALUES (?, ?, 1, ?, ?)", (id_ven, nombre, sucursal, id_prov))
                if foto_url: cursor.execute("INSERT INTO FOTOS_VENDEDOR VALUES (?, ?, ?)", (id_ven + 1000, foto_url, id_ven))
            conn.commit()
            return True, "Guardado"
        except Exception as e: return False, str(e)
        finally: conn.close()
    
    def get_provinces(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id_provincia, nombreProvincia FROM PROVINCIAS")
        return cursor.fetchall()
"""

code_vendors_ui = """from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView, QFormLayout, QFrame, QMessageBox, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt
from controllers.vendor_controller import VendorController
from utils.helpers import load_image_from_url

class VendorsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = VendorController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout()
        left_panel = QFrame()
        l_layout = QVBoxLayout(left_panel)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar Vendedor...")
        self.search.textChanged.connect(self.load_data)
        l_layout.addWidget(self.search)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Sucursal", "Provincia"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill_form)
        l_layout.addWidget(self.table)
        
        right_panel = QFrame()
        right_panel.setFixedWidth(400)
        r_layout = QVBoxLayout(right_panel)
        title = QLabel("Ficha Vendedor")
        title.setProperty("class", "Header")
        r_layout.addWidget(title)
        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(150, 150)
        self.lbl_photo.setStyleSheet("border: 2px dashed #ccc;")
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.addWidget(self.lbl_photo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form = QFormLayout()
        self.inp_id = QSpinBox()
        self.inp_id.setRange(1, 99999)
        self.inp_name = QLineEdit()
        self.inp_sucursal = QLineEdit()
        self.cb_prov = QComboBox()
        self.inp_url = QLineEdit()
        self.inp_url.setPlaceholderText("URL Foto")
        self.inp_url.textChanged.connect(self.preview_photo)
        form.addRow("ID:", self.inp_id)
        form.addRow("Nombre:", self.inp_name)
        form.addRow("Sucursal:", self.inp_sucursal)
        form.addRow("Provincia:", self.cb_prov)
        form.addRow("URL Foto:", self.inp_url)
        r_layout.addLayout(form)
        
        btn_box = QHBoxLayout()
        self.btn_new = QPushButton("Nuevo (+)")
        self.btn_new.clicked.connect(self.new_vendor)
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("successBtn")
        self.btn_save.clicked.connect(self.save_vendor)
        btn_box.addWidget(self.btn_new)
        btn_box.addWidget(self.btn_save)
        r_layout.addLayout(btn_box)
        r_layout.addStretch()
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        self.setLayout(main_layout)
        
        provs = self.controller.get_provinces()
        for p in provs: self.cb_prov.addItem(p[1], p[0])

    def load_data(self):
        data = self.controller.get_all(self.search.text())
        self.table.setRowCount(0)
        self.full_data = data
        for i, row in enumerate(data):
            self.table.insertRow(i)
            from PyQt6.QtWidgets import QTableWidgetItem
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))
            self.table.setItem(i, 2, QTableWidgetItem(row[2]))
            self.table.setItem(i, 3, QTableWidgetItem(row[3]))

    def fill_form(self, item):
        row_idx = item.row()
        vid = int(self.table.item(row_idx, 0).text())
        record = next((r for r in self.full_data if r[0] == vid), None)
        if record:
            self.inp_id.setValue(record[0])
            self.inp_name.setText(record[1])
            self.inp_sucursal.setText(record[2])
            self.cb_prov.setCurrentText(record[3])
            self.inp_url.setText(record[4])
            self.preview_photo()

    def new_vendor(self):
        self.inp_id.setValue(self.controller.get_next_id())
        self.inp_name.clear()
        self.inp_sucursal.clear()
        self.inp_url.clear()
        self.lbl_photo.clear()

    def save_vendor(self):
        ok, msg = self.controller.save(self.inp_id.value(), self.inp_name.text(), self.inp_sucursal.text(), self.cb_prov.currentData(), self.inp_url.text())
        if ok: self.load_data(); QMessageBox.information(self, "OK", msg)
        else: QMessageBox.warning(self, "Error", msg)

    def preview_photo(self):
        url = self.inp_url.text()
        pix = load_image_from_url(url, (150, 150))
        self.lbl_photo.setPixmap(pix)
"""

code_products_ui = """from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView, QFormLayout, QFrame, QMessageBox, QCheckBox, QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from controllers.products_controller import ProductController
from utils.helpers import load_image_from_url
from database import db

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        left_frame = QFrame()
        l_layout = QVBoxLayout(left_frame)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Buscar por nombre, ID o código...")
        self.search.textChanged.connect(self.load_data)
        l_layout.addWidget(self.search)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Stock", "Precio", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill_form)
        l_layout.addWidget(self.table)
        
        right_frame = QFrame()
        right_frame.setFixedWidth(450)
        r_layout = QVBoxLayout(right_frame)
        lbl_header = QLabel("Detalle Producto")
        lbl_header.setProperty("class", "Header")
        r_layout.addWidget(lbl_header)
        self.lbl_img = QLabel("Sin Foto")
        self.lbl_img.setFixedSize(200, 200)
        self.lbl_img.setStyleSheet("border: 2px solid #ddd; background: #fff;")
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.addWidget(self.lbl_img, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form = QFormLayout()
        self.inp_id = QSpinBox()
        self.inp_id.setRange(1, 999999)
        self.inp_name = QLineEdit()
        self.inp_stock = QSpinBox()
        self.inp_stock.setRange(-1000, 10000)
        self.inp_price = QDoubleSpinBox()
        self.inp_price.setMaximum(1000000)
        self.inp_url = QLineEdit()
        self.inp_url.setPlaceholderText("URL de Imagen")
        self.inp_url.textChanged.connect(self.preview_img)
        form.addRow("ID:", self.inp_id)
        form.addRow("Nombre:", self.inp_name)
        form.addRow("Stock:", self.inp_stock)
        form.addRow("Precio Venta:", self.inp_price)
        form.addRow("Foto URL:", self.inp_url)
        r_layout.addLayout(form)
        
        btns = QHBoxLayout()
        self.btn_new = QPushButton("Nuevo (+)")
        self.btn_new.clicked.connect(self.new_product)
        self.btn_save = QPushButton("Guardar Cambios")
        self.btn_save.setObjectName("successBtn")
        self.btn_save.clicked.connect(self.save_product)
        btns.addWidget(self.btn_new)
        btns.addWidget(self.btn_save)
        r_layout.addLayout(btns)
        r_layout.addStretch()
        layout.addWidget(left_frame, 2)
        layout.addWidget(right_frame, 1)
        self.setLayout(layout)

    def load_data(self):
        term = self.search.text()
        prods = self.controller.get_all_products(term)
        self.table.setRowCount(0)
        for i, row in enumerate(prods):
            self.table.insertRow(i)
            from PyQt6.QtWidgets import QTableWidgetItem
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))
            stock = row[2]
            item_stock = QTableWidgetItem(str(stock))
            if stock <= 10: item_stock.setBackground(QColor("#ffcccc")); item_stock.setForeground(QColor("#cc0000"))
            self.table.setItem(i, 2, item_stock)
            self.table.setItem(i, 3, QTableWidgetItem(f"{row[4]:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem("Activo"))

    def fill_form(self, item):
        row = item.row()
        pid = int(self.table.item(row, 0).text())
        data = self.controller.get_product_by_id(pid)
        if data:
            self.inp_id.setValue(data[0])
            self.inp_name.setText(data[1])
            self.inp_stock.setValue(data[2])
            self.inp_price.setValue(float(data[4]))
            self.inp_url.setText("")
            self.lbl_img.setText("Cargando...")
            
    def new_product(self):
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("SELECT ISNULL(MAX(ID_PRODUCTO), 0) + 1 FROM PRODUCTO")
        next_id = cur.fetchone()[0]
        conn.close()
        self.inp_id.setValue(next_id)
        self.inp_name.clear()
        self.inp_stock.setValue(0)
        self.inp_price.setValue(0)
        self.inp_url.clear()
        self.lbl_img.clear()
        self.inp_name.setFocus()

    def save_product(self):
        ok, msg = self.controller.update_product(self.inp_id.value(), self.inp_name.text(), self.inp_stock.value(), 0, self.inp_price.value(), True)
        if ok: QMessageBox.information(self, "OK", msg); self.load_data()
        else: QMessageBox.warning(self, "Error", msg)

    def preview_img(self):
        url = self.inp_url.text()
        pix = load_image_from_url(url, (200, 200))
        self.lbl_img.setPixmap(pix)
"""

code_pos_ui = """from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QTableWidget, QHeaderView, QMessageBox, QGroupBox, QGridLayout, QFrame, QLineEdit, QCompleter)
from PyQt6.QtCore import Qt, QStringListModel
from controllers.sales_controller import SalesController

class POSWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_id = user_data[0]
        self.controller = SalesController()
        self.init_ui()
        self.load_catalogs()

    def init_ui(self):
        layout = QHBoxLayout()
        control_panel = QFrame()
        control_panel.setFixedWidth(400)
        c_layout = QVBoxLayout(control_panel)
        header = QLabel("Facturación (POS)")
        header.setProperty("class", "Header")
        c_layout.addWidget(header)
        c_layout.addWidget(QLabel("Cliente:"))
        self.cb_client = QComboBox()
        self.cb_client.setEditable(True)
        self.cb_client.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        c_layout.addWidget(self.cb_client)
        c_layout.addWidget(QLabel("Producto:"))
        self.cb_prod = QComboBox()
        self.cb_prod.setEditable(True)
        self.cb_prod.currentIndexChanged.connect(self.on_prod_change)
        c_layout.addWidget(self.cb_prod)
        self.lbl_info = QLabel("Stock: - | Precio: -")
        self.lbl_info.setStyleSheet("color: #0056b3; font-weight: bold;")
        c_layout.addWidget(self.lbl_info)
        qty_box = QHBoxLayout()
        self.sp_qty = QSpinBox()
        self.sp_qty.setRange(1, 1000)
        self.sp_qty.valueChanged.connect(self.update_subtotal)
        qty_box.addWidget(QLabel("Cantidad:"))
        qty_box.addWidget(self.sp_qty)
        c_layout.addLayout(qty_box)
        grid = QGridLayout()
        self.cb_pay = QComboBox()
        self.cb_pay.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        self.cb_del = QComboBox()
        self.cb_del.addItems(["Tienda", "Delivery"])
        grid.addWidget(QLabel("Pago:"), 0, 0)
        grid.addWidget(self.cb_pay, 0, 1)
        grid.addWidget(QLabel("Entrega:"), 1, 0)
        grid.addWidget(self.cb_del, 1, 1)
        c_layout.addLayout(grid)
        self.lbl_total = QLabel("RD$ 0.00")
        self.lbl_total.setStyleSheet("font-size: 30px; color: #28a745; font-weight: bold; padding: 10px; border: 2px solid #28a745; border-radius: 5px;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(self.lbl_total)
        self.btn_add = QPushButton("PROCESAR VENTA (F5)")
        self.btn_add.setObjectName("successBtn")
        self.btn_add.setMinimumHeight(60)
        self.btn_add.clicked.connect(self.process)
        c_layout.addWidget(self.btn_add)
        c_layout.addStretch()
        right_panel = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto", "Cant", "Precio", "Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_panel.addWidget(self.table)
        layout.addWidget(control_panel)
        layout.addLayout(right_panel)
        self.setLayout(layout)

    def load_catalogs(self):
        clients = self.controller.get_clients()
        self.cb_client.clear()
        for c in clients: self.cb_client.addItem(f"{c[1]} {c[2]} ({c[3]})", c[0])
        prods = self.controller.get_products()
        self.cb_prod.clear()
        self.products_map = {}
        for p in prods:
            self.cb_prod.addItem(f"{p[1]}", p[0])
            self.products_map[p[0]] = p

    def on_prod_change(self):
        pid = self.cb_prod.currentData()
        if pid in self.products_map:
            p = self.products_map[pid]
            self.lbl_info.setText(f"Stock: {p[3]}  |  Precio: RD$ {p[2]:,.2f}")
            self.update_subtotal()

    def update_subtotal(self):
        pid = self.cb_prod.currentData()
        if pid in self.products_map:
            price = float(self.products_map[pid][2])
            qty = self.sp_qty.value()
            total = price * qty * 1.18
            self.lbl_total.setText(f"RD$ {total:,.2f}")

    def process(self):
        pid = self.cb_prod.currentData()
        cid = self.cb_client.currentData()
        qty = self.sp_qty.value()
        if not pid or not cid: QMessageBox.warning(self, "Error", "Seleccione Cliente y Producto"); return
        confirm = QMessageBox.question(self, "Confirmar", "¿Procesar Factura?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            pay_method = self.cb_pay.currentIndex() + 1
            del_method = self.cb_del.currentIndex() + 1
            ok, msg = self.controller.process_sale(cid, self.user_id, pid, qty, pay_method, del_method)
            if ok: QMessageBox.information(self, "Venta Exitosa", msg); self.load_catalogs()
            else: QMessageBox.critical(self, "Error", msg)
"""

code_main_window = """from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame)
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
        title = QLabel("SUPERMERCADO\nJPV")
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
"""

files = {
    "utils/helpers.py": code_helpers,
    "controllers/vendor_controller.py": code_vendor_controller,
    "views/vendors_ui.py": code_vendors_ui,
    "views/inventory_ui.py": code_products_ui,
    "views/pos_ui.py": code_pos_ui,
    "views/main_window_ui.py": code_main_window
}

if not os.path.exists("utils"): os.makedirs("utils")
for path, content in files.items():
    try:
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        print(f"✅ Actualizado: {path}")
    except Exception as e: print(f"❌ Error en {path}: {e}")
