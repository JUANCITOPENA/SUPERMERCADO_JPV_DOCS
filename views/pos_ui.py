from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QTableWidget, QHeaderView, QMessageBox, QGroupBox, QGridLayout, QFrame, QLineEdit, QCompleter)
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
