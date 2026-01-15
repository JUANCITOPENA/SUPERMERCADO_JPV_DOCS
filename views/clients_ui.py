from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QHeaderView, 
                             QFormLayout, QFrame, QMessageBox, QComboBox, QDoubleSpinBox, QCheckBox)
from controllers.client_controller import ClientController

class ClientsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ClientController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # --- List ---
        list_frame = QFrame()
        list_layout = QVBoxLayout(list_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar cliente (Nombre o RNC)...")
        self.search_input.textChanged.connect(self.load_data)
        list_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "RNC", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill_form)
        list_layout.addWidget(self.table)
        
        # --- Form ---
        form_frame = QFrame()
        form_frame.setFixedWidth(400)
        form_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        
        title = QLabel("Gestión de Clientes")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        form_layout.addWidget(title)

        self.form = QFormLayout()
        
        self.inp_name = QLineEdit()
        self.inp_lastname = QLineEdit()
        self.inp_rnc = QLineEdit()
        self.inp_rnc.setPlaceholderText("9 u 11 dígitos")
        
        self.cb_type = QComboBox()
        self.cb_type.addItems(["FISICA", "JURIDICA"])
        
        self.cb_region = QComboBox()
        self.cb_prov = QComboBox()
        
        self.load_geo()
        self.cb_region.currentIndexChanged.connect(self.update_provinces)

        self.inp_address = QLineEdit()
        
        self.chk_credit = QCheckBox("Crédito Aprobado")
        self.inp_limit = QDoubleSpinBox()
        self.inp_limit.setMaximum(1000000)

        self.form.addRow("Nombre:", self.inp_name)
        self.form.addRow("Apellido:", self.inp_lastname)
        self.form.addRow("RNC/Cédula:", self.inp_rnc)
        self.form.addRow("Tipo:", self.cb_type)
        self.form.addRow("Región:", self.cb_region)
        self.form.addRow("Provincia:", self.cb_prov)
        self.form.addRow("Dirección:", self.inp_address)
        self.form.addRow(self.chk_credit)
        self.form.addRow("Límite Crédito:", self.inp_limit)
        
        form_layout.addLayout(self.form)
        
        self.btn_save = QPushButton("Guardar Nuevo")
        self.btn_save.setObjectName("successBtn")
        self.btn_save.clicked.connect(self.save_client)
        
        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.clicked.connect(self.clear_form)
        
        form_layout.addWidget(self.btn_save)
        form_layout.addWidget(self.btn_clear)
        form_layout.addStretch()

        layout.addWidget(list_frame, 2)
        layout.addWidget(form_frame, 1)
        self.setLayout(layout)

    def load_geo(self):
        regions = self.controller.get_regions()
        for r in regions:
            self.cb_region.addItem(r[1], r[0])

    def update_provinces(self):
        self.cb_prov.clear()
        region_id = self.cb_region.currentData()
        if region_id:
            provs = self.controller.get_provinces_by_region(region_id)
            for p in provs:
                self.cb_prov.addItem(p[1], p[0])

    def load_data(self):
        term = self.search_input.text()
        clients = self.controller.get_all_clients(term)
        self.table.setRowCount(0)
        for row_idx, row in enumerate(clients):
            self.table.insertRow(row_idx)
            from PyQt6.QtWidgets import QTableWidgetItem
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{row[1]} {row[2]}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[3]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row[4]))

    def fill_form(self, item):
        # Simplification: Only fill key fields for edit or show details
        # Since the SP only updates Address and Limit, we focus on that for edits
        # But here I will just reset to "New" mode because full edit wasn't requested in SP
        pass

    def clear_form(self):
        self.inp_name.clear()
        self.inp_lastname.clear()
        self.inp_rnc.clear()
        self.inp_address.clear()
        self.inp_limit.setValue(0)
        self.chk_credit.setChecked(False)

    def save_client(self):
        name = self.inp_name.text()
        lname = self.inp_lastname.text()
        rnc = self.inp_rnc.text()
        
        if len(rnc) not in [9, 11]:
            QMessageBox.warning(self, "Error", "El RNC debe tener 9 u 11 dígitos")
            return

        success, msg = self.controller.create_client(
            name, lname, rnc, 
            self.cb_type.currentText(),
            self.cb_region.currentData(),
            self.cb_prov.currentData(),
            self.inp_address.text(),
            self.chk_credit.isChecked(),
            self.inp_limit.value()
        )
        
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", msg)
