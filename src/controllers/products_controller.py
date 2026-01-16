from src.config.database import db
class ProductController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        # Added PRECIO_COMPRA at the end
        sql = "SELECT P.ID_PRODUCTO, P.PRODUCTO, P.STOCK, P.PRECIO_VENTA, ISNULL(FP.foto_Productos_url, ''), P.PRECIO_COMPRA FROM PRODUCTO P LEFT JOIN FOTO_PRODUCTOS FP ON P.ID_PRODUCTO=FP.ID_PRODUCTO"
        if search: sql += f" WHERE P.PRODUCTO LIKE '%{search}%' OR CAST(P.ID_PRODUCTO AS VARCHAR) LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res
        
    def save(self, id_p, nom, stock, pc, pv, url):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_p: # Update logic if ID exists? Or check existence
                cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_PRODUCTO=?", (id_p,))
                if cursor.fetchone()[0] > 0:
                     cursor.execute("UPDATE PRODUCTO SET PRODUCTO=?, STOCK=?, PRECIO_COMPRA=?, PRECIO_VENTA=? WHERE ID_PRODUCTO=?", (nom, stock, pc, pv, id_p))
                else:
                     cursor.execute("INSERT INTO PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA) VALUES (?,?,?,?,?)", (id_p, nom, stock, pc, pv))
            else:
                # Generate ID
                cursor.execute("SELECT ISNULL(MAX(ID_PRODUCTO),0)+1 FROM PRODUCTO")
                id_p = cursor.fetchone()[0]
                cursor.execute("INSERT INTO PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA) VALUES (?,?,?,?,?)", (id_p, nom, stock, pc, pv))
            
            # Photo
            cursor.execute("DELETE FROM FOTO_PRODUCTOS WHERE ID_PRODUCTO=?", (id_p,))
            if url: 
                # ID_Foto logic? Just random or max + 1
                cursor.execute("SELECT ISNULL(MAX(ID_Foto),0)+1 FROM FOTO_PRODUCTOS")
                idf = cursor.fetchone()[0]
                cursor.execute("INSERT INTO FOTO_PRODUCTOS (ID_Foto, foto_Productos_url, ID_PRODUCTO) VALUES (?,?,?)", (idf, url, id_p))
            
            conn.commit()
            return True, "Guardado"
        except Exception as e: return False, str(e)
        finally: conn.close()

    def delete(self, pid):
        conn = db.connect()
        cursor = conn.cursor()
        try:
             cursor.execute("DELETE FROM FOTO_PRODUCTOS WHERE ID_PRODUCTO=?", (pid,))
             cursor.execute("DELETE FROM PRODUCTO WHERE ID_PRODUCTO=?", (pid,))
             conn.commit()
             return True, "Eliminado"
        except Exception as e: return False, str(e)
        finally: conn.close()
