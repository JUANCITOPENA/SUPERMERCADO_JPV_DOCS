from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QHeaderView, 
                             QFormLayout, QFrame, QMessageBox, QCheckBox, QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt
from controllers.products_controller import ProductController

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # --- Left Panel: List ---
        list_frame = QFrame()
        list_layout = QVBoxLayout(list_frame)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(self.search_input)
        list_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Stock", "Precio Venta", "ITBIS?"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill_form)
        list_layout.addWidget(self.table)
        
        # --- Right Panel: Form ---
        form_frame = QFrame()
        form_frame.setFixedWidth(350)
        form_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        
        title = QLabel("Gestión de Producto")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        form_layout.addWidget(title)

        self.form_layout = QFormLayout()
        
        self.inp_id = QSpinBox()
        self.inp_id.setRange(1, 999999)
        
        self.inp_name = QLineEdit()
        self.inp_stock = QSpinBox()
        self.inp_stock.setRange(-1000, 10000)
        
        self.inp_cost = QDoubleSpinBox()
        self.inp_cost.setMaximum(999999.99)
        
        self.inp_price = QDoubleSpinBox()
        self.inp_price.setMaximum(999999.99)
        
        self.chk_tax = QCheckBox("Gravado ITBIS")
        self.chk_tax.setChecked(True)

        self.form_layout.addRow("ID:", self.inp_id)
        self.form_layout.addRow("Nombre:", self.inp_name)
        self.form_layout.addRow("Stock:", self.inp_stock)
        self.form_layout.addRow("Costo:", self.inp_cost)
        self.form_layout.addRow("Precio Venta:", self.inp_price)
        self.form_layout.addRow("", self.chk_tax)
        
        form_layout.addLayout(self.form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("successBtn")
        self.btn_save.clicked.connect(self.save_product)
        
        self.btn_delete = QPushButton("Eliminar")
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.clicked.connect(self.delete_product)
        
        self.btn_clear = QPushButton("Nuevo")
        self.btn_clear.clicked.connect(self.clear_form)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        form_layout.addLayout(btn_layout)
        form_layout.addWidget(self.btn_clear)
        form_layout.addStretch()

        layout.addWidget(list_frame, 2)
        layout.addWidget(form_frame, 1)
        self.setLayout(layout)

    def load_data(self):
        term = self.search_input.text()
        products = self.controller.get_all_products(term)
        self.table.setRowCount(0)
        for row_idx, row in enumerate(products):
            self.table.insertRow(row_idx)
            # ID, Name, Stock, Cost, Price
            from PyQt6.QtWidgets import QTableWidgetItem
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1])))
            
            stock_item = QTableWidgetItem(str(row[2]))
            if row[2] <= 10:
                stock_item.setBackground(Qt.GlobalColor.red)
                stock_item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(row_idx, 2, stock_item)
            
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"RD$ {row[4]:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem("Sí")) # Placeholder for Gravado visual

    def fill_form(self, item):
        row = item.row()
        id_prod = int(self.table.item(row, 0).text())
        data = self.controller.get_product_by_id(id_prod)
        if data:
            self.inp_id.setValue(data[0])
            self.inp_id.setEnabled(False) # ID cannot be changed on edit
            self.inp_name.setText(data[1])
            self.inp_stock.setValue(data[2])
            self.inp_cost.setValue(float(data[3]))
            self.inp_price.setValue(float(data[4]))
            self.chk_tax.setChecked(bool(data[5]))
            self.btn_save.setText("Actualizar")

    def clear_form(self):
        self.inp_id.setEnabled(True)
        self.inp_id.setValue(0)
        self.inp_name.clear()
        self.inp_stock.setValue(0)
        self.inp_cost.setValue(0)
        self.inp_price.setValue(0)
        self.btn_save.setText("Guardar")

    def save_product(self):
        p_id = self.inp_id.value()
        name = self.inp_name.text()
        stock = self.inp_stock.value()
        cost = self.inp_cost.value()
        price = self.inp_price.value()
        tax = self.chk_tax.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return

        if self.btn_save.text() == "Guardar":
            success, msg = self.controller.create_product(p_id, name, stock, cost, price, tax)
        else:
            success, msg = self.controller.update_product(p_id, name, stock, cost, price, tax)
            
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", msg)

    def delete_product(self):
        p_id = self.inp_id.value()
        confirm = QMessageBox.question(self, "Eliminar", "¿Seguro que desea eliminar?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = self.controller.delete_product(p_id)
            if success:
                self.load_data()
                self.clear_form()
            else:
                QMessageBox.critical(self, "Error", msg)
