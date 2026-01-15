from database import db
import pyodbc
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter
import os

class ReportController:
    def get_sales_report_data(self):
        conn = db.connect()
        cursor = conn.cursor()
        # Using the view created in the script
        cursor.execute("SELECT TOP 100 ID_PEDIDO, FECHA, Cliente, RNC_CEDULA, NCF_GENERADO, VENTA_BRUTA FROM VISTA_ANALITICA_DETALLADA ORDER BY FECHA DESC")
        data = cursor.fetchall()
        conn.close()
        return data

    def generate_pdf_report(self, filepath):
        data = self.get_sales_report_data()
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Reporte de Ventas - Supermercado JPV")
        
        c.setFont("Helvetica", 10)
        y = height - 80
        headers = ["ID", "Fecha", "Cliente", "NCF", "Total"]
        x_positions = [50, 100, 220, 380, 500]
        
        for i, h in enumerate(headers):
            c.drawString(x_positions[i], y, h)
            
        y -= 20
        c.line(50, y+15, 550, y+15)
        
        for row in data:
            if y < 50:
                c.showPage()
                y = height - 50
            
            c.drawString(x_positions[0], y, str(row.ID_PEDIDO))
            c.drawString(x_positions[1], y, str(row.FECHA)[:10])
            c.drawString(x_positions[2], y, str(row.Cliente)[:25])
            c.drawString(x_positions[3], y, str(row.NCF_GENERADO))
            c.drawString(x_positions[4], y, f"RD$ {row.VENTA_BRUTA:,.2f}")
            y -= 15
            
        c.save()
        return True

    def generate_excel_report(self, filepath):
        data = self.get_sales_report_data()
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet()
        
        headers = ["ID Venta", "Fecha", "Cliente", "RNC", "NCF", "Total"]
        bold = workbook.add_format({'bold': True})
        
        for col, h in enumerate(headers):
            worksheet.write(0, col, h, bold)
            
        for row_idx, row in enumerate(data, start=1):
            worksheet.write(row_idx, 0, row.ID_PEDIDO)
            worksheet.write(row_idx, 1, str(row.FECHA))
            worksheet.write(row_idx, 2, row.Cliente)
            worksheet.write(row_idx, 3, row.RNC_CEDULA)
            worksheet.write(row_idx, 4, row.NCF_GENERADO)
            worksheet.write(row_idx, 5, float(row.VENTA_BRUTA))
            
        workbook.close()
        return True
