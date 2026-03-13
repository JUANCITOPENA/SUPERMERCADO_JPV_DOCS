from src.config.database import db
import pandas as pd
import os
from datetime import datetime

class ReportController:
    def export_to_excel(self, data, headers, filename="export.xlsx"):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            path = os.path.join(desktop, filename)
            
            # Ensure data matches headers length
            if data and len(data[0]) != len(headers):
                return False, f"Error interno: Columnas ({len(data[0])}) vs Headers ({len(headers)})"

            df = pd.DataFrame(data, columns=headers)
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reporte')
                worksheet = writer.sheets['Reporte']
                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_len, 50)
            return True, f"Exportado exitosamente a:\n{path}"
        except Exception as e:
            return False, str(e)

    def get_client_stats(self, client_id):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT COUNT(DISTINCT V.ID_VENTA), ISNULL(SUM(DV.SUBTOTAL), 0),
                   ISNULL(SUM(DV.CANTIDAD * P.PRECIO_COMPRA), 0),
                   ISNULL(SUM(DV.SUBTOTAL - (DV.CANTIDAD * P.PRECIO_COMPRA)), 0)
            FROM VENTAS V
            JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA
            JOIN PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
            WHERE V.ID_CLIENTE = ? AND V.ESTADO = 'COMPLETADA'
        """
        cursor.execute(sql, (client_id,))
        row = cursor.fetchone()
        conn.close()
        v = float(row[1]) if row[1] else 0.0
        m = float(row[3]) if row[3] else 0.0
        p = (m/v*100) if v > 0 else 0
        return {"compras": row[0], "venta": v, "costo": float(row[2]), "margen_moneda": m, "margen_porc": p}

    def get_client_history(self, client_id):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT V.ID_VENTA, V.FECHA, V.NCF_GENERADO, V.TOTAL_VENTA, COUNT(DV.ID_DETALLE)
            FROM VENTAS V
            LEFT JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA
            WHERE V.ID_CLIENTE = ?
            GROUP BY V.ID_VENTA, V.FECHA, V.NCF_GENERADO, V.TOTAL_VENTA
            ORDER BY V.FECHA DESC
        """
        cursor.execute(sql, (client_id,))
        return cursor.fetchall()

    def get_vendor_stats(self, vendor_id):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT COUNT(DISTINCT V.ID_VENTA), ISNULL(SUM(DV.SUBTOTAL), 0),
                   ISNULL(SUM(DV.SUBTOTAL - (DV.CANTIDAD * P.PRECIO_COMPRA)), 0)
            FROM VENTAS V
            JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA
            JOIN PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
            WHERE V.ID_VENDEDOR = ? AND V.ESTADO = 'COMPLETADA'
        """
        cursor.execute(sql, (vendor_id,))
        row = cursor.fetchone()
        conn.close()
        return {"ventas": row[0], "total_neto": float(row[1]), "ganancia": float(row[2])}

    def get_inventory_valuation(self):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT SUM(STOCK), SUM(STOCK*PRECIO_COMPRA), SUM(STOCK*PRECIO_VENTA), SUM((PRECIO_VENTA-PRECIO_COMPRA)*STOCK) FROM PRODUCTO"
        cursor.execute(sql)
        row = cursor.fetchone()
        conn.close()
        return list(row) if row else [0,0,0,0]

    def get_product_rentability(self):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT 
                ID_PRODUCTO, 
                PRODUCTO, 
                PRECIO_COMPRA, 
                PRECIO_VENTA, 
                (PRECIO_VENTA - PRECIO_COMPRA), 
                CASE WHEN PRECIO_VENTA > 0 THEN ((PRECIO_VENTA - PRECIO_COMPRA)/PRECIO_VENTA)*100 ELSE 0 END
            FROM PRODUCTO
        """
        cursor.execute(sql)
        return [list(row) for row in cursor.fetchall()]

    def get_vendors_list_report(self):
        conn = db.connect()
        cursor = conn.cursor()
        
        # Determine Date Range for Narrative (Min/Max date in sales)
        cursor.execute("SELECT MIN(FECHA), MAX(FECHA) FROM VENTAS WHERE ESTADO='COMPLETADA'")
        dates = cursor.fetchone()
        date_narrative = "Histórico Global"
        if dates[0] and dates[1]:
            date_narrative = f"Datos del {dates[0]} al {dates[1]}"

        # Main Query
        sql = """
            SELECT 
                V.ID_VENDEDOR, 
                V.VENDEDOR, 
                V.SUCURSAL, 
                P.nombreProvincia, 
                ISNULL(FV.foto_Vendedor_url, ''),
                ISNULL(SUM(DV.SUBTOTAL), 0) as Ingresos,
                ISNULL(SUM(DV.CANTIDAD * PR.PRECIO_COMPRA), 0) as Costos
            FROM VENDEDOR V
            LEFT JOIN PROVINCIAS P ON V.PROVINCIA = P.id_provincia
            LEFT JOIN FOTOS_VENDEDOR FV ON V.ID_VENDEDOR = FV.ID_vendedor
            LEFT JOIN VENTAS VE ON V.ID_VENDEDOR = VE.ID_VENDEDOR AND VE.ESTADO = 'COMPLETADA'
            LEFT JOIN DETALLE_VENTAS DV ON VE.ID_VENTA = DV.ID_VENTA
            LEFT JOIN PRODUCTO PR ON DV.ID_PRODUCTO = PR.ID_PRODUCTO
            GROUP BY V.ID_VENDEDOR, V.VENDEDOR, V.SUCURSAL, P.nombreProvincia, FV.foto_Vendedor_url
        """
        cursor.execute(sql)
        raw_data = cursor.fetchall()
        
        final_data = []
        total_rev = 0
        total_cost = 0
        
        for row in raw_data:
            rev = float(row[5])
            cost = float(row[6])
            margin = rev - cost
            margin_p = (margin / rev * 100) if rev > 0 else 0
            
            total_rev += rev
            total_cost += cost
            
            final_data.append(list(row[:5]) + [rev, cost, margin, margin_p])
            
        conn.close()
        
        # Summary Totals
        total_margin = total_rev - total_cost
        total_margin_p = (total_margin / total_rev * 100) if total_rev > 0 else 0
        
        summary = {
            "Total Ingresos": total_rev,
            "Total Costos": total_cost,
            "Total Margen": total_margin,
            "Margen Global %": total_margin_p
        }
        
        return final_data, summary, date_narrative

    def get_products_list_report(self):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT P.ID_PRODUCTO, P.PRODUCTO, P.STOCK, P.PRECIO_VENTA, ISNULL(FP.foto_Productos_url, '')
            FROM PRODUCTO P
            LEFT JOIN FOTO_PRODUCTOS FP ON P.ID_PRODUCTO = FP.ID_PRODUCTO
        """
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def get_product_performance_stats(self):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT 
                P.PRODUCTO,
                SUM(DV.CANTIDAD) as TotalVendida,
                SUM(DV.SUBTOTAL) as IngresoTotal,
                SUM(DV.CANTIDAD * P.PRECIO_COMPRA) as CostoTotal
            FROM DETALLE_VENTAS DV
            JOIN PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
            JOIN VENTAS V ON DV.ID_VENTA = V.ID_VENTA
            WHERE V.ESTADO = 'COMPLETADA'
            GROUP BY P.PRODUCTO
            ORDER BY IngresoTotal DESC
        """
        cursor.execute(sql)
        data = []
        for row in cursor.fetchall():
            prod = row[0]
            qty = row[1]
            rev = float(row[2])
            cost = float(row[3])
            margin = rev - cost
            margin_p = (margin / rev * 100) if rev > 0 else 0
            data.append([prod, qty, rev, cost, margin, margin_p])
        
        conn.close()
        return data

    def get_client_account_statement(self, client_id):
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get Client Info
        cursor.execute("SELECT NOMBRE_CLIENTE + ' ' + APELLIDO_CLIENTE, RNC_CEDULA, DIRECCION FROM CLIENTE WHERE ID_CLIENTE=?", (client_id,))
        client = cursor.fetchone()
        
        # Get Transactions (Sales only for now as no Payment table exists)
        # We assume Sales are Debits (Cargos)
        # To simulate a Statement, we assume "Contado" sales are immediately paid (Credit=Debit), 
        # and "Credito" sales are unpaid (Credit=0).
        
        sql = """
            SELECT 
                V.FECHA,
                V.NCF_GENERADO,
                'FACTURA DE VENTA' as CONCEPTO,
                V.TOTAL_VENTA as CARGO,
                CASE WHEN CP.ES_CREDITO = 1 THEN 0 ELSE V.TOTAL_VENTA END as ABONO,
                CP.NOMBRE_CONDICION
            FROM VENTAS V
            JOIN CONDICION_PAGO CP ON V.ID_CONDICION = CP.ID_CONDICION
            WHERE V.ID_CLIENTE = ? AND V.ESTADO = 'COMPLETADA'
            ORDER BY V.FECHA ASC
        """
        cursor.execute(sql, (client_id,))
        raw_txns = cursor.fetchall()
        
        processed_txns = []
        running_balance = 0.0
        
        for row in raw_txns:
            date = row[0]
            ref = row[1]
            desc = row[2] + f" ({row[5]})"
            debit = float(row[3])
            credit = float(row[4])
            
            # Logic: Balance increases with Debit (Purchase), decreases with Credit (Payment)
            # If it's a "Contado" sale, Debit=Credit, so Balance change is 0.
            # If it's a "Credito" sale, Credit=0, so Balance increases.
            
            running_balance += (debit - credit)
            
            processed_txns.append([
                date.strftime("%d/%m/%Y"),
                ref,
                desc,
                debit,
                credit,
                running_balance
            ])
            
        conn.close()
        
        return {
            "client_name": client[0],
            "client_rnc": client[1],
            "client_addr": client[2],
            "transactions": processed_txns,
            "final_balance": running_balance
        }
