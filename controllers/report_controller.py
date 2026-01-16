from database import db
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
        sql = """
            SELECT V.ID_VENDEDOR, V.VENDEDOR, V.SUCURSAL, P.nombreProvincia, ISNULL(FV.foto_Vendedor_url, '')
            FROM VENDEDOR V
            LEFT JOIN PROVINCIAS P ON V.PROVINCIA = P.id_provincia
            LEFT JOIN FOTOS_VENDEDOR FV ON V.ID_VENDEDOR = FV.ID_vendedor
        """
        cursor.execute(sql)
        return cursor.fetchall()
        
    def get_products_list_report(self):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT P.ID_PRODUCTO, P.PRODUCTO, P.STOCK, P.PRECIO_VENTA, ISNULL(FP.foto_Productos_url, '')
            FROM PRODUCTO P
            LEFT JOIN FOTO_PRODUCTOS FP ON P.ID_PRODUCTO = FP.ID_PRODUCTO
        """
        cursor.execute(sql)
        return cursor.fetchall()
