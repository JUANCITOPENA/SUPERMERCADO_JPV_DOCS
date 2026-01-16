from src.config.database import db

class ClientController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT C.ID_CLIENTE, C.NOMBRE_CLIENTE, C.APELLIDO_CLIENTE, C.RNC_CEDULA, C.TIPO_PERSONA, 
                   C.DIRECCION, C.TIENE_CREDITO_APROBADO, C.LIMITE_CREDITO,
                   R.REGION, P.nombreProvincia, C.id_region, C.id_provincia
            FROM CLIENTE C
            LEFT JOIN REGION R ON C.id_region = R.ID_REGION
            LEFT JOIN PROVINCIAS P ON C.id_provincia = P.id_provincia
        """
        if search:
            sql += f" WHERE C.NOMBRE_CLIENTE LIKE '%{search}%' OR C.RNC_CEDULA LIKE '%{search}%' OR C.APELLIDO_CLIENTE LIKE '%{search}%'"
        
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def get_geo(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_REGION, REGION FROM REGION")
        regs = cursor.fetchall()
        cursor.execute("SELECT id_provincia, nombreProvincia, id_region FROM PROVINCIAS")
        provs = cursor.fetchall()
        conn.close()
        return regs, provs

    def delete(self, client_id):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # Check for dependencies? The DB might have constraints.
            cursor.execute("DELETE FROM CLIENTE WHERE ID_CLIENTE = ?", (client_id,))
            conn.commit()
            return True, "Cliente eliminado."
        except Exception as e:
            return False, f"Error al eliminar: {e}"
        finally:
            conn.close()

    def save(self, id_c, nom, ape, rnc, tipo, region_id, prov_id, direccion, credito, limite):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_c: # Update
                sql = """
                    UPDATE CLIENTE SET 
                    NOMBRE_CLIENTE=?, APELLIDO_CLIENTE=?, RNC_CEDULA=?, TIPO_PERSONA=?,
                    id_region=?, id_provincia=?, DIRECCION=?, TIENE_CREDITO_APROBADO=?, LIMITE_CREDITO=?
                    WHERE ID_CLIENTE=?
                """
                cursor.execute(sql, (nom, ape, rnc, tipo, region_id, prov_id, direccion, credito, limite, id_c))
            else: # Insert
                # Get max ID
                cursor.execute("SELECT ISNULL(MAX(ID_CLIENTE),0) + 1 FROM CLIENTE")
                new_id = cursor.fetchone()[0]
                sql = """
                    INSERT INTO CLIENTE (ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, RNC_CEDULA, TIPO_PERSONA, 
                                         id_region, id_provincia, DIRECCION, TIENE_CREDITO_APROBADO, LIMITE_CREDITO)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """
                cursor.execute(sql, (new_id, nom, ape, rnc, tipo, region_id, prov_id, direccion, credito, limite))
            
            conn.commit()
            return True, "Cliente guardado."
        except Exception as e:
            return False, f"Error al guardar: {e}"
        finally:
            conn.close()
