from database import db

class VendorController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        # Added P.id_provincia, V.id_genero
        sql = """
            SELECT V.ID_VENDEDOR, V.VENDEDOR, V.SUCURSAL, P.nombreProvincia, 
                   ISNULL(FV.foto_Vendedor_url, ''), P.id_provincia, V.id_genero
            FROM VENDEDOR V 
            LEFT JOIN PROVINCIAS P ON V.PROVINCIA = P.id_provincia 
            LEFT JOIN FOTOS_VENDEDOR FV ON V.ID_VENDEDOR = FV.ID_vendedor
        """
        if search: sql += f" WHERE V.VENDEDOR LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def get_geo(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id_provincia, nombreProvincia FROM PROVINCIAS")
        return cursor.fetchall()

    def save(self, id_v, nom, sucursal, id_prov, id_gen, url):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_v: 
                cursor.execute("SELECT COUNT(*) FROM VENDEDOR WHERE ID_VENDEDOR=?", (id_v,))
                if cursor.fetchone()[0] > 0:
                    cursor.execute("UPDATE VENDEDOR SET VENDEDOR=?, SUCURSAL=?, PROVINCIA=?, id_genero=? WHERE ID_VENDEDOR=?", (nom, sucursal, id_prov, id_gen, id_v))
                else:
                     cursor.execute("INSERT INTO VENDEDOR (ID_VENDEDOR, VENDEDOR, id_genero, SUCURSAL, PROVINCIA) VALUES (?,?,?,?,?)", (id_v, nom, id_gen, sucursal, id_prov))
            else:
                 cursor.execute("SELECT ISNULL(MAX(ID_VENDEDOR),0)+1 FROM VENDEDOR")
                 id_v = cursor.fetchone()[0]
                 cursor.execute("INSERT INTO VENDEDOR (ID_VENDEDOR, VENDEDOR, id_genero, SUCURSAL, PROVINCIA) VALUES (?,?,?,?,?)", (id_v, nom, id_gen, sucursal, id_prov))
            
            cursor.execute("DELETE FROM FOTOS_VENDEDOR WHERE ID_vendedor=?", (id_v,))
            if url:
                cursor.execute("SELECT ISNULL(MAX(ID_Foto),0)+1 FROM FOTOS_VENDEDOR")
                idf = cursor.fetchone()[0]
                cursor.execute("INSERT INTO FOTOS_VENDEDOR (ID_Foto, foto_Vendedor_url, ID_vendedor) VALUES (?,?,?)", (idf, url, id_v))
            
            conn.commit()
            return True, "Guardado"
        except Exception as e: return False, str(e)
        finally: conn.close()

    def delete(self, vid):
        conn = db.connect()
        cursor = conn.cursor()
        try:
             cursor.execute("DELETE FROM FOTOS_VENDEDOR WHERE ID_vendedor=?", (vid,))
             cursor.execute("DELETE FROM VENDEDOR WHERE ID_VENDEDOR=?", (vid,))
             conn.commit()
             return True, "Eliminado"
        except Exception as e: return False, str(e)
        finally: conn.close()