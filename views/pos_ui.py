
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
