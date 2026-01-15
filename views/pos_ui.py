from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QSpinBox, QPushButton, QTableWidget, 
                             QHeaderView, QMessageBox, QGroupBox, QFormLayout, QFrame, QLineEdit)
from PyQt6.QtCore import Qt
from controllers.sales_controller import SalesController

class POSWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_id = user_data[0] # ID del vendedor logueado
        self.controller = SalesController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Panel Izquierdo (Controles) ---
        left_panel = QFrame()
        left_panel.setFixedWidth(400)
        left_panel.setStyleSheet("background-color: white; border-radius: 10px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        title = QLabel("Nueva Venta")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        left_layout.addWidget(title)
        
        # Cliente
        lbl_cli = QLabel("Cliente:")
        lbl_cli.setProperty("class", "FormLabel")
        self.cb_clients = QComboBox()
        self.cb_clients.setEditable(True) # Permitir buscar escribiendo
        left_layout.addWidget(lbl_cli)
        left_layout.addWidget(self.cb_clients)

        # Producto
        lbl_prod = QLabel("Producto:")
        lbl_prod.setProperty("class", "FormLabel")
        self.cb_products = QComboBox()
        self.cb_products.setEditable(True)
        left_layout.addWidget(lbl_prod)
        left_layout.addWidget(self.cb_products)

        # Cantidad y Stock
        qty_layout = QHBoxLayout()
        self.sp_qty = QSpinBox()
        self.sp_qty.setRange(1, 1000)
        self.sp_qty.setFixedHeight(35)
        
        self.lbl_stock = QLabel("Stock: -")
        self.lbl_stock.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        
        qty_layout.addWidget(QLabel("Cantidad:"))
        qty_layout.addWidget(self.sp_qty)
        qty_layout.addStretch()
        qty_layout.addWidget(self.lbl_stock)
        left_layout.addLayout(qty_layout)

        # Pago y Entrega
        form_grid = QGridLayout()
        self.cb_payment = QComboBox()
        self.cb_payment.addItems(["Efectivo (1)", "Tarjeta (2)", "Transferencia (3)", "Cheque (4)"])
        
        self.cb_delivery = QComboBox()
        self.cb_delivery.addItems(["Tienda (1)", "Delivery (2)", "Envío Nacional (3)"])

        form_grid.addWidget(QLabel("Método Pago:"), 0, 0)
        form_grid.addWidget(self.cb_payment, 0, 1)
        form_grid.addWidget(QLabel("Entrega:"), 1, 0)
        form_grid.addWidget(self.cb_delivery, 1, 1)
        left_layout.addLayout(form_grid)
        
        # Totales (Simulados visualmente antes de agregar)
        self.lbl_total_preview = QLabel("Total Est: RD$ 0.00")
        self.lbl_total_preview.setStyleSheet("font-size: 18px; color: #27ae60; font-weight: bold; align: center;")
        self.lbl_total_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.lbl_total_preview)

        left_layout.addStretch()
        
        btn_process = QPushButton("FACTURAR E IMPRIMIR (F5)")
        btn_process.setObjectName("successBtn")
        btn_process.setMinimumHeight(50)
        btn_process.clicked.connect(self.process_transaction)
        left_layout.addWidget(btn_process)

        # --- Panel Derecho (Tabla / Carrito) ---
        right_panel = QVBoxLayout()
        
        lbl_cart = QLabel("Carrito de Compras (Vista Previa)")
        lbl_cart.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_panel.addWidget(lbl_cart)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto", "Cant", "Precio Unit.", "Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_panel.addWidget(self.table)
        
        main_layout.addWidget(left_panel)
        main_layout.addLayout(right_panel)
        
        self.setLayout(main_layout)
        
        # Conexiones
        self.cb_products.currentIndexChanged.connect(self.update_stock_label)
        self.sp_qty.valueChanged.connect(self.update_total_preview)

    def load_data(self):
        self.cb_clients.clear()
        clients = self.controller.get_clients()
        for c in clients:
            self.cb_clients.addItem(f"{c[1]} {c[2]} ({c[3]})", c[0])

        self.cb_products.clear()
        self.products_data = self.controller.get_products() # List of tuples
        for p in self.products_data:
            # p: (ID, Name, Price, Stock)
            self.cb_products.addItem(f"{p[1]} - RD${p[2]}", p[0])

    def update_stock_label(self):
        idx = self.cb_products.currentIndex()
        if idx >= 0:
            stock = self.products_data[idx][3]
            self.lbl_stock.setText(f"Stock: {stock}")
            self.update_total_preview()

    def update_total_preview(self):
        idx = self.cb_products.currentIndex()
        if idx >= 0:
            price = self.products_data[idx][2]
            qty = self.sp_qty.value()
            total = price * qty * 1.18 # Aprox with tax
            self.lbl_total_preview.setText(f"Total Est: RD$ {total:,.2f}")

    def process_transaction(self):
        client_id = self.cb_clients.currentData()
        product_id = self.cb_products.currentData()
        qty = self.sp_qty.value()
        
        if not client_id or not product_id:
            QMessageBox.warning(self, "Error", "Seleccione Cliente y Producto")
            return

        payment_method = self.cb_payment.currentIndex() + 1
        delivery_method = self.cb_delivery.currentIndex() + 1
        
        confirm = QMessageBox.question(self, "Confirmar Venta", "¿Procesar factura?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = self.controller.process_sale(client_id, self.user_id, product_id, qty, payment_method, delivery_method)
            
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.load_data() # Refresh stock
            else:
                QMessageBox.critical(self, "Error", message)

