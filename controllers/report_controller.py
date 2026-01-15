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
