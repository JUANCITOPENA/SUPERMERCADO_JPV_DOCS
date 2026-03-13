
from src.config.database import db
import datetime

class SalesController:
    def get_clients(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_CLIENTE, NOMBRE_CLIENTE + ' ' + APELLIDO_CLIENTE, RNC_CEDULA, TIPO_PERSONA FROM CLIENTE").fetchall()
        conn.close()
        return res

    def get_products(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_PRODUCTO, PRODUCTO, PRECIO_VENTA, STOCK FROM PRODUCTO WHERE STOCK > 0").fetchall()
        conn.close()
        return res

    def get_payment_methods(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_METODO, METODO FROM METODO_PAGO").fetchall()
        conn.close()
        return res

    def get_delivery_methods(self):
        conn = db.connect()
        res = conn.cursor().execute("SELECT ID_ENTREGA, TIPO_ENTREGA FROM METODO_ENTREGA").fetchall()
        conn.close()
        return res

    def get_all_sales(self, filters=None):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT V.ID_VENTA, V.FECHA, C.NOMBRE_CLIENTE + ' ' + C.APELLIDO_CLIENTE, 
                   V.NCF_GENERADO, V.TOTAL_VENTA, V.ESTADO, VD.VENDEDOR
            FROM VENTAS V
            JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
            JOIN VENDEDOR VD ON V.ID_VENDEDOR = VD.ID_VENDEDOR
        """
        params = []
        conditions = []
        
        if filters:
            if filters.get('search'):
                s = f"%{filters['search']}%"
                conditions.append("(C.NOMBRE_CLIENTE LIKE ? OR V.NCF_GENERADO LIKE ? OR CAST(V.ID_VENTA AS VARCHAR) LIKE ?)")
                params.extend([s, s, s])
            if filters.get('date_from'):
                conditions.append("V.FECHA >= ?")
                params.append(filters['date_from'])
            if filters.get('date_to'):
                conditions.append("V.FECHA <= ?")
                params.append(filters['date_to'])

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY V.FECHA DESC"
        
        cursor.execute(sql, tuple(params))
        res = cursor.fetchall()
        conn.close()
        return res

    def get_sale_full_detail(self, sale_id):
        conn = db.connect()
        cursor = conn.cursor()
        
        # 1. Header info extended
        sql_head = """
            SELECT V.ID_VENTA, V.NCF_GENERADO, TN.DESCRIPCION as TIPO_NCF,
                   C.NOMBRE_CLIENTE + ' ' + C.APELLIDO_CLIENTE, C.RNC_CEDULA,
                   V.SUBTOTAL_VENTA, V.TOTAL_ITBIS, V.TOTAL_VENTA,
                   CP.NOMBRE_CONDICION, MP.METODO
            FROM VENTAS V
            JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
            JOIN TIPO_NCF TN ON V.ID_TIPO_NCF = TN.ID_TIPO_NCF
            JOIN CONDICION_PAGO CP ON V.ID_CONDICION = CP.ID_CONDICION
            JOIN METODO_PAGO MP ON V.ID_METODO_PAGO = MP.ID_METODO
            WHERE V.ID_VENTA = ?
        """
        cursor.execute(sql_head, (sale_id,))
        head = cursor.fetchone()
        
        if not head:
            conn.close()
            return None, []

        # 2. Items
        sql_items = """
            SELECT P.PRODUCTO, DV.CANTIDAD, DV.PRECIO_UNITARIO, DV.SUBTOTAL
            FROM DETALLE_VENTAS DV
            JOIN PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
            WHERE DV.ID_VENTA = ?
        """
        cursor.execute(sql_items, (sale_id,))
        items = []
        for row in cursor.fetchall():
            items.append({
                "name": row[0],
                "qty": row[1],
                "price": float(row[2]),
                "total": float(row[3])
            })
            
        conn.close()
        
        sale_data = {
            "id": head[0],
            "ncf": head[1],
            "ncf_type": head[2],
            "client_name": head[3],
            "client_rnc": head[4],
            "subtotal": float(head[5]),
            "itbis": float(head[6]),
            "total": float(head[7]),
            "payment_cond": head[8],
            "payment_method": head[9]
        }
        
        return sale_data, items

    def cancel_sale(self, sale_id):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # 1. Check status
            cursor.execute("SELECT ESTADO FROM VENTAS WHERE ID_VENTA=?", (sale_id,))
            status = cursor.fetchone()[0]
            if status == 'CANCELADA':
                return False, "La venta ya está cancelada."

            # 2. Return Stock
            cursor.execute("SELECT ID_PRODUCTO, CANTIDAD FROM DETALLE_VENTAS WHERE ID_VENTA=?", (sale_id,))
            items = cursor.fetchall()
            for pid, qty in items:
                cursor.execute("UPDATE PRODUCTO SET STOCK = STOCK + ? WHERE ID_PRODUCTO=?", (qty, pid))
            
            # 3. Update Status
            cursor.execute("UPDATE VENTAS SET ESTADO = 'CANCELADA' WHERE ID_VENTA=?", (sale_id,))
            conn.commit()
            return True, "Venta anulada y stock retornado."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def process_full_sale(self, client_id, vendor_id, items, pay_id, del_id, total, subtotal, itbis):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # 1. Get Client Info for NCF and Credit Logic
            cursor.execute("SELECT TIPO_PERSONA, id_region, TIENE_CREDITO_APROBADO FROM CLIENTE WHERE ID_CLIENTE=?", (client_id,))
            crow = cursor.fetchone()
            c_type, region_id, has_credit = crow[0], crow[1], crow[2]

            # 2. Determine NCF
            if c_type == 'JURIDICA':
                ncf_type_id = 1 # E31
                serie = 'E31'
            else:
                ncf_type_id = 2 # E32
                serie = 'E32'
            
            # Sequence
            cursor.execute("SELECT COUNT(*) FROM VENTAS WHERE NCF_GENERADO LIKE ?", (f"{serie}%",))
            seq = cursor.fetchone()[0] + 1
            ncf_full = f"{serie}{seq:010d}"

            # 3. Determine Payment Condition
            # Simplified Logic: If Payment Method is 'Cheque' (4) or 'Transferencia' (3) AND Client has credit, assume Credit condition?
            # Or just default to Contado unless specified. 
            # User requirement: "Condición de Pago" on ticket.
            # Let's map Payment Method ID to Condition ID for simplicity in this prototype
            # METODO_PAGO: 1=Efectivo, 2=Tarjeta, 3=Transferencia, 4=Cheque
            # CONDICION_PAGO: 1=Contado, 2=Cred 15, 3=Cred 30
            
            cond_id = 1 # Contado by default
            if pay_id == 4: # Cheque -> Assume Credit 30 days for business logic simulation
                 cond_id = 3
            
            # 4. Insert Header
            sql_head = """
                INSERT INTO VENTAS (FECHA, ID_CLIENTE, ID_VENDEDOR, ID_REGION, ID_CONDICION, ID_METODO_PAGO, ID_ENTREGA, ID_TIPO_NCF, NCF_GENERADO, SUBTOTAL_VENTA, TOTAL_ITBIS, TOTAL_VENTA, ESTADO)
                VALUES (GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETADA')
            """
            cursor.execute(sql_head, (client_id, vendor_id, region_id, cond_id, pay_id, del_id, ncf_type_id, ncf_full, subtotal, itbis, total))
            cursor.execute("SELECT @@IDENTITY")
            sale_id = cursor.fetchone()[0]

            # 5. Insert Details
            for item in items:
                pid = item['id']
                qty = item['qty']
                price = item['price']
                line_itbis = item['itbis_unit']
                line_sub = item['price'] * qty
                
                # Check Stock
                cursor.execute("SELECT STOCK FROM PRODUCTO WHERE ID_PRODUCTO=?", (pid,))
                stock = cursor.fetchone()[0]
                if stock < qty:
                    raise Exception(f"Stock insuficiente para producto ID {pid}")

                sql_det = """
                    INSERT INTO DETALLE_VENTAS (ID_VENTA, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO, ITBIS_UNITARIO, SUBTOTAL)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql_det, (sale_id, pid, qty, price, line_itbis, line_sub))
                
                # Update Stock
                cursor.execute("UPDATE PRODUCTO SET STOCK = STOCK - ? WHERE ID_PRODUCTO=?", (qty, pid))

            conn.commit()
            
            # Fetch human readable names for ticket
            cursor.execute("SELECT DESCRIPCION FROM TIPO_NCF WHERE ID_TIPO_NCF=?", (ncf_type_id,))
            ncf_name = cursor.fetchone()[0]
            
            cursor.execute("SELECT NOMBRE_CONDICION FROM CONDICION_PAGO WHERE ID_CONDICION=?", (cond_id,))
            cond_name = cursor.fetchone()[0]
            
            return True, {
                "id": sale_id, "ncf": ncf_full, "ncf_type": ncf_name, "payment_cond": cond_name
            }
            
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
