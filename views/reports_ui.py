from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox, QFileDialog)
from controllers.report_controller import ReportController

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ReportController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("Centro de Reportes")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        desc = QLabel("Seleccione el formato para exportar el reporte de Ventas:")
        layout.addWidget(desc)
        
        btn_layout = QHBoxLayout()
        
        btn_pdf = QPushButton("Exportar a PDF")
        btn_pdf.setFixedSize(200, 60)
        btn_pdf.setStyleSheet("font-size: 16px;")
        btn_pdf.clicked.connect(self.export_pdf)
        
        btn_excel = QPushButton("Exportar a Excel")
        btn_excel.setFixedSize(200, 60)
        btn_excel.setStyleSheet("font-size: 16px;")
        btn_excel.clicked.connect(self.export_excel)
        
        btn_layout.addWidget(btn_pdf)
        btn_layout.addWidget(btn_excel)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "ReporteVentas.pdf", "PDF Files (*.pdf)")
        if path:
            if self.controller.generate_pdf_report(path):
                QMessageBox.information(self, "Éxito", "Reporte PDF generado correctamente.")

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "ReporteVentas.xlsx", "Excel Files (*.xlsx)")
        if path:
            if self.controller.generate_excel_report(path):
                QMessageBox.information(self, "Éxito", "Reporte Excel generado correctamente.")
