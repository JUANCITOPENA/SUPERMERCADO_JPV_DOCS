
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
