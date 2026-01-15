from database import db
import pyodbc

class ProductController:
    def get_all_products(self, search_term=""):
        conn = db.connect()
        if not conn: return []
        cursor = conn.cursor()
        query = "SELECT ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA FROM PRODUCTO"
        if search_term:
            query += " WHERE PRODUCTO LIKE ?"
            cursor.execute(query, (f"%{search_term}%",))
        else:
            cursor.execute(query)
        
        products = cursor.fetchall()
        conn.close()
        return products

    def get_product_by_id(self, id):
        conn = db.connect()
        if not conn: return None
        cursor = conn.cursor()
        cursor.execute("SELECT ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA, GRAVADO_ITBIS FROM PRODUCTO WHERE ID_PRODUCTO = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def create_product(self, id_prod, name, stock, p_compra, p_venta, gravado=True):
        conn = db.connect()
        if not conn: return False, "No hay conexión"
        cursor = conn.cursor()
        try:
            # Check if ID exists
            cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_PRODUCTO = ?", (id_prod,))
            if cursor.fetchone()[0] > 0:
                return False, "El ID del producto ya existe."

            sql = """
            INSERT INTO PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA, GRAVADO_ITBIS)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (id_prod, name, stock, p_compra, p_venta, 1 if gravado else 0))
            conn.commit()
            return True, "Producto creado exitosamente."
        except pyodbc.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def update_product(self, id_prod, name, stock, p_compra, p_venta, gravado=True):
        conn = db.connect()
        if not conn: return False, "No hay conexión"
        cursor = conn.cursor()
        try:
            sql = """
            UPDATE PRODUCTO SET PRODUCTO=?, STOCK=?, PRECIO_COMPRA=?, PRECIO_VENTA=?, GRAVADO_ITBIS=?
            WHERE ID_PRODUCTO=?
            """
            cursor.execute(sql, (name, stock, p_compra, p_venta, 1 if gravado else 0, id_prod))
            conn.commit()
            return True, "Producto actualizado exitosamente."
        except pyodbc.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_product(self, id_prod):
        conn = db.connect()
        if not conn: return False, "No hay conexión"
        cursor = conn.cursor()
        try:
            # Check dependencies? The DB might have FKs but let's try
            cursor.execute("DELETE FROM PRODUCTO WHERE ID_PRODUCTO = ?", (id_prod,))
            conn.commit()
            return True, "Producto eliminado."
        except pyodbc.Error as e:
            return False, f"Error al eliminar (posiblemente tiene ventas asociadas): {e}"
        finally:
            conn.close()
