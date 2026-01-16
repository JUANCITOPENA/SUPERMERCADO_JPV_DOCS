
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import os
import datetime
import requests
import tempfile
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

class PrintEngine:
    @staticmethod
    def _download_image_temp(url):
        if not url or url == 'N/A' or url == '':
            return None
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                fd, path = tempfile.mkstemp(suffix=".png")
                with os.fdopen(fd, 'wb') as tmp:
                    tmp.write(res.content)
                return path
        except:
            pass
        return None

    @staticmethod
    def generate_invoice(sale_data, items, filename=None, is_copy=False, user_reprint=""):
        if not filename:
            filename = f"factura_{sale_data['ncf']}.pdf"
            
        c = canvas.Canvas(filename, pagesize=letter)
        w, h = letter
        
        # --- WATERMARK ---
        if is_copy:
            c.saveState()
            c.translate(w/2, h/2)
            c.rotate(45)
            c.setFont("Helvetica-Bold", 80)
            c.setFillColor(colors.lightgrey) # CORREGIDO: setFillColor
            c.drawCentredString(0, 0, "COPIA - REIMPRESIÓN")
            c.restoreState()
            
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.black)
            c.drawString(20*mm, 10*mm, f"Reimpreso por: {user_reprint} el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # --- HEADER BACKGROUND ---
        c.setFillColor(colors.navy)
        c.rect(0, h - 35*mm, w, 35*mm, fill=1, stroke=0)
        
        # --- TITLE INFO ---
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(20*mm, h - 15*mm, "SUPERMERCADO JPV V6")
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, h - 22*mm, "RNC: 101-00000-1 | Tel: 809-555-5555")
        c.drawString(20*mm, h - 28*mm, "Santo Domingo, República Dominicana")

        # --- CLIENT & SALE INFO ---
        c.setFillColor(colors.black)
        
        c.setStrokeColor(colors.grey)
        c.roundRect(15*mm, h - 70*mm, 185*mm, 30*mm, 4, stroke=1, fill=0)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, h - 45*mm, "FACTURA NO:")
        c.drawString(20*mm, h - 52*mm, "FECHA:")
        c.drawString(20*mm, h - 59*mm, "CLIENTE:")
        c.drawString(20*mm, h - 66*mm, "RNC CLIENTE:")
        
        c.setFont("Helvetica", 10)
        c.drawString(50*mm, h - 45*mm, str(sale_data['id']))
        c.drawString(50*mm, h - 52*mm, datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
        c.drawString(50*mm, h - 59*mm, str(sale_data['client_name'])[:35])
        c.drawString(50*mm, h - 66*mm, str(sale_data['client_rnc']))
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(110*mm, h - 45*mm, "NCF:")
        c.drawString(110*mm, h - 52*mm, "TIPO:")
        c.drawString(110*mm, h - 59*mm, "CONDICIÓN:")
        
        c.setFont("Helvetica", 10)
        c.drawString(135*mm, h - 45*mm, str(sale_data['ncf']))
        c.drawString(135*mm, h - 52*mm, str(sale_data['ncf_type'])[:25])
        c.drawString(135*mm, h - 59*mm, str(sale_data.get('payment_cond', 'Contado')))
        
        # --- ITEMS TABLE HEADER ---
        y = h - 80*mm
        c.setFillColor(colors.lightgrey)
        c.rect(15*mm, y, 185*mm, 8*mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        
        c.drawString(20*mm, y+2*mm, "CANT")
        c.drawString(40*mm, y+2*mm, "DESCRIPCIÓN")
        c.drawString(130*mm, y+2*mm, "PRECIO UNIT")
        c.drawString(160*mm, y+2*mm, "TOTAL")
        
        y -= 6*mm
        c.setFont("Helvetica", 9)
        
        for item in items:
            c.drawString(20*mm, y, str(item['qty']))
            c.drawString(40*mm, y, item['name'][:45])
            c.drawString(130*mm, y, f"{item['price']:,.2f}")
            c.drawString(160*mm, y, f"{item['total']:,.2f}")
            
            c.setStrokeColor(colors.lightgrey)
            c.line(15*mm, y-2*mm, 200*mm, y-2*mm) 
            
            y -= 6*mm
            if y < 30*mm: 
                c.showPage()
                y = h - 20*mm
        
        y -= 5*mm
        c.setStrokeColor(colors.black)
        c.line(110*mm, y, 200*mm, y) 
        y -= 5*mm
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(110*mm, y, "SUBTOTAL:")
        c.drawRightString(190*mm, y, f"{sale_data['subtotal']:,.2f}")
        y -= 6*mm
        
        c.drawString(110*mm, y, "ITBIS (18%):")
        c.drawRightString(190*mm, y, f"{sale_data['itbis']:,.2f}")
        y -= 6*mm
        
        c.setFillColor(colors.navy)
        c.rect(110*mm, y-2*mm, 85*mm, 8*mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(112*mm, y, "TOTAL A PAGAR:")
        c.drawRightString(190*mm, y, f"{sale_data['total']:,.2f}")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Oblique", 8)
        msg = "COPIA SIN VALOR TRIBUTARIO" if is_copy else "ORIGINAL: VÁLIDO PARA CRÉDITO FISCAL"
        c.drawCentredString(w/2, 15*mm, msg)
        
        try:
            c.save()
            os.startfile(filename) 
            return True, "Impreso correctamente"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_simple_list_pdf(title, data, columns, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        table_data = [columns] + data
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ]))
        
        try:
            doc.build(elements)
            os.startfile(filename)
            return True, "Reporte generado correctamente"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_advanced_catalog_pdf(title, data, columns, summary_data, date_narrative, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title & Dates
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Periodo de Datos:</b> {date_narrative}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Main Table
        table_data = [columns]
        for row in data:
            # Row Structure: ID, Name, Branch, Prov, URL, Rev, Cost, Marg, Marg%
            row_list = list(row)
            
            # Handle Image (Index 4)
            img_url = row_list[4]
            img_path = PrintEngine._download_image_temp(img_url)
            if img_path:
                img = RLImage(img_path, width=15*mm, height=15*mm)
                row_list[4] = img
            else:
                row_list[4] = "Sin Foto"
                
            # Format Financials (Indices 5,6,7,8)
            row_list[5] = f"${row_list[5]:,.2f}" # Rev
            row_list[6] = f"${row_list[6]:,.2f}" # Cost
            row_list[7] = f"${row_list[7]:,.2f}" # Marg
            row_list[8] = f"{row_list[8]:.2f}%"  # %
            
            table_data.append(row_list)
            
        t = Table(table_data, colWidths=[10*mm, 40*mm, 25*mm, 25*mm, 20*mm, 25*mm, 25*mm, 25*mm, 15*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 7),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Summary Section
        elements.append(Paragraph("Resumen Financiero Global", styles['Heading2']))
        
        sum_data = [
            ["Concepto", "Total"],
            ["Total Ingresos", f"${summary_data['Total Ingresos']:,.2f}"],
            ["Total Costos", f"${summary_data['Total Costos']:,.2f}"],
            ["Total Margen Bruto", f"${summary_data['Total Margen']:,.2f}"],
            ["% Margen Global", f"{summary_data['Margen Global %']:.2f}%"]
        ]
        
        t_sum = Table(sum_data, colWidths=[60*mm, 40*mm])
        t_sum.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        
        elements.append(t_sum)
        
        try:
            doc.build(elements)
            os.startfile(filename)
            return True, "Reporte generado correctamente"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_account_statement_pdf(data, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(Paragraph("Estado de Cuenta de Cliente", styles['Title']))
        elements.append(Paragraph(f"Fecha de Emisión: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Client Info Box
        c_info = [
            [Paragraph(f"<b>Cliente:</b> {data['client_name']}", styles['Normal'])],
            [Paragraph(f"<b>RNC/Cédula:</b> {data['client_rnc']}", styles['Normal'])],
            [Paragraph(f"<b>Dirección:</b> {data['client_addr'] or 'N/A'}", styles['Normal'])]
        ]
        t_info = Table(c_info, colWidths=[180*mm])
        t_info.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 20))
        
        # Transactions Table
        headers = ["Fecha", "Referencia", "Concepto", "Cargos", "Abonos", "Saldo"]
        table_rows = [headers]
        
        total_cargos = 0
        total_abonos = 0
        
        for tx in data['transactions']:
            # tx: Date, Ref, Desc, Debit, Credit, Bal
            row = [
                tx[0],
                tx[1],
                tx[2],
                f"{tx[3]:,.2f}",
                f"{tx[4]:,.2f}",
                f"{tx[5]:,.2f}"
            ]
            table_rows.append(row)
            total_cargos += tx[3]
            total_abonos += tx[4]
            
        t = Table(table_rows, colWidths=[25*mm, 35*mm, 60*mm, 25*mm, 25*mm, 25*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (3,0), (-1,-1), 'RIGHT'), # Numbers right aligned
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Summary
        sum_data = [
            ["Resumen General", ""],
            ["Total Facturado (Cargos):", f"{total_cargos:,.2f}"],
            ["Total Pagado (Abonos):", f"{total_abonos:,.2f}"],
            ["Saldo Pendiente Actual:", f"{data['final_balance']:,.2f}"]
        ]
        
        t_sum = Table(sum_data, colWidths=[80*mm, 40*mm])
        t_sum.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t_sum)
        
        try:
            doc.build(elements)
            os.startfile(filename)
            return True, "Estado de Cuenta generado."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_catalog_pdf(title, data, columns, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        table_data = [columns]
        
        for row in data:
            row_list = list(row)
            img_url = row_list[-1]
            img_path = PrintEngine._download_image_temp(img_url)
            if img_path:
                img = RLImage(img_path, width=20*mm, height=20*mm)
                row_list[-1] = img 
            else:
                row_list[-1] = "Sin Foto"
            table_data.append(row_list)
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        
        elements.append(t)
        doc.build(elements)
        os.startfile(filename)

    @staticmethod
    def generate_profile_pdf(title, info_dict, img_url, stats_dict, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 20))
        
        img_path = PrintEngine._download_image_temp(img_url)
        img_flowable = RLImage(img_path, width=60*mm, height=60*mm) if img_path else Paragraph("Sin Foto", styles['Normal'])
        
        info_text = []
        for k, v in info_dict.items():
            info_text.append([Paragraph(f"<b>{k}:</b>", styles['Normal']), Paragraph(str(v), styles['Normal'])])
            
        t_info = Table(info_text, colWidths=[40*mm, 80*mm])
        t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        
        master_data = [[img_flowable, t_info]]
        t_master = Table(master_data, colWidths=[70*mm, 120*mm])
        t_master.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (0,0), 1, colors.grey),
            ('LEFTPADDING', (1,0), (1,0), 20),
        ]))
        elements.append(t_master)
        elements.append(Spacer(1, 30))
        
        elements.append(Paragraph("Estadísticas de Desempeño", styles['Heading2']))
        stats_data = [[k, v] for k, v in stats_dict.items()]
        t_stats = Table(stats_data, colWidths=[80*mm, 50*mm])
        t_stats.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t_stats)
        
        doc.build(elements)
        os.startfile(filename)

    @staticmethod
    def generate_performance_pdf(title, data, columns, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # --- Table ---
        # Format data for table display (currency/decimals)
        table_display = [columns]
        # data format: [Prod, Qty, Rev, Cost, Marg, Marg%]
        chart_data = []
        chart_labels = []
        
        for i, row in enumerate(data):
            # Take top 10 for chart
            if i < 10:
                chart_labels.append(row[0][:15]) # Truncate name
                chart_data.append(row[2]) # Revenue
                
            formatted_row = [
                row[0],
                str(row[1]),
                f"{row[2]:,.2f}",
                f"{row[3]:,.2f}",
                f"{row[4]:,.2f}",
                f"{row[5]:.1f}%"
            ]
            table_display.append(formatted_row)
            
        t = Table(table_display)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'), # Numbers right aligned
            ('ALIGN', (0,0), (0,-1), 'LEFT'),   # Names left aligned
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))
        
        # --- Chart (Top 10 Revenue) ---
        if chart_data:
            elements.append(Paragraph("Top 10 Productos por Ingresos", styles['Heading2']))
            
            d = Drawing(400, 200)
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300
            bc.data = [chart_data]
            bc.strokeColor = colors.black
            bc.valueAxis.valueMin = 0
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.dx = 8
            bc.categoryAxis.labels.dy = -2
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.categoryNames = chart_labels
            bc.bars[0].fillColor = colors.blue
            
            d.add(bc)
            elements.append(d)

        try:
            doc.build(elements)
            os.startfile(filename)
            return True, "Reporte generado correctamente"
        except Exception as e:
            return False, str(e)
