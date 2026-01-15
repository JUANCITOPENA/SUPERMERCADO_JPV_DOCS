from database import db
import pyodbc

class SalesController:
    def get_products(self):
        """Obtener lista de productos para el combo box"""
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_PRODUCTO, PRODUCTO, PRECIO_VENTA, STOCK FROM PRODUCTO WHERE STOCK > 0")
        products = cursor.fetchall()
        conn.close()
        return products

    def get_clients(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, RNC_CEDULA FROM CLIENTE")
        clients = cursor.fetchall()
        conn.close()
        return clients

    def process_sale(self, client_id, seller_id, product_id, qty, pay_method, delivery_method):
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            # Llamada al Procedimiento Almacenado de SQL Server
            sql = """
            EXEC SP_FACTURAR_VENTA 
                @ID_Cliente = ?, 
                @ID_Vendedor = ?, 
                @ID_Producto = ?, 
                @Cantidad = ?, 
                @ID_MetodoPago = ?, 
                @ID_Entrega = ?
            """
            cursor.execute(sql, (client_id, seller_id, product_id, qty, pay_method, delivery_method))
            conn.commit()
            return True, "Venta procesada correctamente. Stock descontado y NCF generado."
        except pyodbc.Error as ex:
            # Capturamos el mensaje de error del Trigger o del SP
            sql_state = ex.args[0]
            error_msg = ex.args[1]
            # Limpiamos el mensaje crudo de ODBC
            clean_msg = error_msg.split(']')[(-1)].strip()
            return False, clean_msg
        finally:
            conn.close()