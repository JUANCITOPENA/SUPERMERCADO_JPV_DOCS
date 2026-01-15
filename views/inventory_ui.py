from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView, QFormLayout, QFrame, QMessageBox, QCheckBox, QDoubleSpinBox, QSpinBox)
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
