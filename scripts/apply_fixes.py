import os

# --- 1. FIXED REPORT CONTROLLER ---
code_report_controller = """from database import db
import pyodbc
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter
import os

class ReportController:
    def get_sales_report_data(self):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # Usamos una consulta segura y convertimos tipos basicos si es necesario
            cursor.execute("SELECT TOP 100 ID_PEDIDO, FECHA, Cliente, RNC_CEDULA, NCF_GENERADO, VENTA_BRUTA FROM VISTA_ANALITICA_DETALLADA ORDER BY FECHA DESC")
            data = cursor.fetchall()
            return data
        except Exception as e:
            print(f"Error SQL Reporte: {e}")
            return []
        finally:
            conn.close()

    def generate_pdf_report(self, filepath):
        data = self.get_sales_report_data()
        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Header
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 50, "Reporte de Ventas - Supermercado JPV")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, "Generado automaticamente por el sistema")
            
            # Table Headers
            y = height - 100
            c.setFont("Helvetica-Bold", 10)
            headers = ["ID", "Fecha", "Cliente", "NCF", "Total"]
            x_pos = [40, 80, 200, 380, 500]
            
            for i, h in enumerate(headers):
                c.drawString(x_pos[i], y, h)
            
            c.line(40, y-5, 570, y-5)
            y -= 20
            
            # Data
            c.setFont("Helvetica", 9)
            total_general = 0.0
            
            for row in data:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                # Conversiones seguras
                fecha_str = str(row.FECHA)[:10] if row.FECHA else ""
                total_float = float(row.VENTA_BRUTA) if row.VENTA_BRUTA else 0.0
                total_general += total_float
                
                c.drawString(x_pos[0], y, str(row.ID_PEDIDO))
                c.drawString(x_pos[1], y, fecha_str)
                c.drawString(x_pos[2], y, str(row.Cliente)[:25])
                c.drawString(x_pos[3], y, str(row.NCF_GENERADO))
                c.drawString(x_pos[4], y, f"RD$ {total_float:,.2f}")
                y -= 15
            
            # Footer Total
            c.line(40, y+10, 570, y+10)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(400, y-5, f"GRAN TOTAL: RD$ {total_general:,.2f}")
                
            c.save()
            return True
        except Exception as e:
            print(f"Error PDF: {e}")
            return False

    def generate_excel_report(self, filepath):
        data = self.get_sales_report_data()
        try:
            workbook = xlsxwriter.Workbook(filepath)
            worksheet = workbook.add_worksheet()
            
            # Formatos
            bold = workbook.add_format({'bold': True, 'bg_color': '#cccccc', 'border': 1})
            money = workbook.add_format({'num_format': '$#,##0.00'})
            date_fmt = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            
            headers = ["ID Venta", "Fecha", "Cliente", "RNC", "NCF", "Total"]
            for col, h in enumerate(headers):
                worksheet.write(0, col, h, bold)
                
            for row_idx, row in enumerate(data, start=1):
                worksheet.write(row_idx, 0, row.ID_PEDIDO)
                worksheet.write(row_idx, 1, str(row.FECHA), date_fmt)
                worksheet.write(row_idx, 2, row.Cliente)
                worksheet.write(row_idx, 3, row.RNC_CEDULA)
                worksheet.write(row_idx, 4, row.NCF_GENERADO)
                # Convertir Decimal a float para Excel
                worksheet.write(row_idx, 5, float(row.VENTA_BRUTA) if row.VENTA_BRUTA else 0.0, money)
                
            workbook.close()
            return True
        except Exception as e:
            print(f"Error Excel: {e}")
            return False
"""

# --- 2. FIXED INVENTORY UI ---
code_inventory_ui = """from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
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
        lbl_search = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre del producto...")
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        list_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Stock", "Precio Venta", "Estado"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.fill_form)
        list_layout.addWidget(self.table)
        
        # --- Right Panel: Form ---
        form_frame = QFrame()
        form_frame.setFixedWidth(350)
        form_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        
        title = QLabel("Gestión de Producto")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
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
            # Row: ID, Prod, Stock, Cost, Price
            
            from PyQt6.QtWidgets import QTableWidgetItem
            from PyQt6.QtGui import QColor
            
            # ID
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            # Nombre
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1])))
            
            # Stock con Alerta Visual
            stock_val = row[2]
            stock_item = QTableWidgetItem(str(stock_val))
            if stock_val <= 10:
                stock_item.setBackground(QColor("#e74c3c")) # Rojo
                stock_item.setForeground(QColor("white"))
            elif stock_val <= 50:
                 stock_item.setBackground(QColor("#f1c40f")) # Amarillo
                 stock_item.setForeground(QColor("black"))
            self.table.setItem(row_idx, 2, stock_item)
            
            # Precio (Conversión Decimal -> Float -> String)
            price_val = float(row[4]) if row[4] else 0.0
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"RD$ {price_val:,.2f}"))
            
            # Estado
            self.table.setItem(row_idx, 4, QTableWidgetItem("Activo"))

    def fill_form(self, item):
        row = item.row()
        try:
            id_prod = int(self.table.item(row, 0).text())
            data = self.controller.get_product_by_id(id_prod)
            if data:
                self.inp_id.setValue(data[0])
                self.inp_id.setEnabled(False) # Bloquear ID en edición
                self.inp_name.setText(data[1])
                self.inp_stock.setValue(data[2])
                self.inp_cost.setValue(float(data[3]))
                self.inp_price.setValue(float(data[4]))
                self.chk_tax.setChecked(bool(data[5]))
                self.btn_save.setText("Actualizar")
        except Exception as e:
            print(f"Error llenando formulario: {e}")

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
        
        if not name:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio")
            return

        if self.btn_save.text() == "Guardar":
            success, msg = self.controller.create_product(p_id, name, self.inp_stock.value(), self.inp_cost.value(), self.inp_price.value(), self.chk_tax.isChecked())
        else:
            success, msg = self.controller.update_product(p_id, name, self.inp_stock.value(), self.inp_cost.value(), self.inp_price.value(), self.chk_tax.isChecked())
            
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error BD", msg)

    def delete_product(self):
        p_id = self.inp_id.value()
        if p_id == 0: return
        
        confirm = QMessageBox.question(self, "Eliminar", f"¿Eliminar producto ID {p_id}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = self.controller.delete_product(p_id)
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.load_data()
                self.clear_form()
            else:
                QMessageBox.critical(self, "Error", msg)
"""

# --- 3. APPLY CHANGES ---
files_to_fix = {
    r"controllers/report_controller.py": code_report_controller,
    r"views/inventory_ui.py": code_inventory_ui
}

for path, content in files_to_fix.items():
    full_path = os.path.join(os.getcwd(), path)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Archivo corregido: {path}")
    except Exception as e:
        print(f"❌ Error escribiendo {path}: {e}")
