from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView, QFormLayout, QFrame, QMessageBox, QComboBox, QSpinBox)
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
