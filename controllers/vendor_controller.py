from database import db
import pyodbc

class VendorController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        query = "SELECT V.ID_VENDEDOR, V.VENDEDOR, V.SUCURSAL, P.nombreProvincia, ISNULL(FV.foto_Vendedor_url, '') FROM VENDEDOR V LEFT JOIN PROVINCIAS P ON V.PROVINCIA = P.id_provincia LEFT JOIN FOTOS_VENDEDOR FV ON V.ID_VENDEDOR = FV.ID_vendedor"
        if search: query += f" WHERE V.VENDEDOR LIKE '%{search}%'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

    def get_next_id(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ISNULL(MAX(ID_VENDEDOR), 0) + 1 FROM VENDEDOR")
        next_id = cursor.fetchone()[0]
        conn.close()
        return next_id

    def save(self, id_ven, nombre, sucursal, id_prov, foto_url):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM VENDEDOR WHERE ID_VENDEDOR = ?", (id_ven,))
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute("UPDATE VENDEDOR SET VENDEDOR=?, SUCURSAL=?, PROVINCIA=? WHERE ID_VENDEDOR=?", (nombre, sucursal, id_prov, id_ven))
                cursor.execute("DELETE FROM FOTOS_VENDEDOR WHERE ID_vendedor=?", (id_ven,))
                if foto_url: cursor.execute("INSERT INTO FOTOS_VENDEDOR VALUES (?, ?, ?)", (id_ven + 1000, foto_url, id_ven))
            else:
                cursor.execute("INSERT INTO VENDEDOR (ID_VENDEDOR, VENDEDOR, id_genero, SUCURSAL, PROVINCIA) VALUES (?, ?, 1, ?, ?)", (id_ven, nombre, sucursal, id_prov))
                if foto_url: cursor.execute("INSERT INTO FOTOS_VENDEDOR VALUES (?, ?, ?)", (id_ven + 1000, foto_url, id_ven))
            conn.commit()
            return True, "Guardado"
        except Exception as e: return False, str(e)
        finally: conn.close()
    
    def get_provinces(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id_provincia, nombreProvincia FROM PROVINCIAS")
        return cursor.fetchall()
