from src.config.database import db

class AuxController:
    # --- REGION ---
    def get_regions(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_REGION, REGION FROM REGION"
        if search:
            sql += f" WHERE REGION LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_region(self, id_reg, nombre):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_reg:
                cursor.execute("UPDATE REGION SET REGION=? WHERE ID_REGION=?", (nombre, id_reg))
            else:
                cursor.execute("SELECT ISNULL(MAX(ID_REGION),0) + 1 FROM REGION")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO REGION (ID_REGION, REGION) VALUES (?,?)", (new_id, nombre))
            conn.commit()
            return True, "Región guardada."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_region(self, id_reg):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM REGION WHERE ID_REGION=?", (id_reg,))
            conn.commit()
            return True, "Región eliminada."
        except Exception as e:
            return False, f"Error (posiblemente en uso): {e}"
        finally:
            conn.close()

    # --- PROVINCIAS ---
    def get_provincias(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
            SELECT P.id_provincia, P.nombreProvincia, R.REGION, P.id_region 
            FROM PROVINCIAS P
            LEFT JOIN REGION R ON P.id_region = R.ID_REGION
        """
        if search:
            sql += f" WHERE P.nombreProvincia LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_provincia(self, id_prov, nombre, id_region):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_prov:
                cursor.execute("UPDATE PROVINCIAS SET nombreProvincia=?, id_region=? WHERE id_provincia=?", (nombre, id_region, id_prov))
            else:
                cursor.execute("SELECT ISNULL(MAX(id_provincia),0) + 1 FROM PROVINCIAS")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO PROVINCIAS (id_provincia, nombreProvincia, id_region) VALUES (?,?,?)", (new_id, nombre, id_region))
            conn.commit()
            return True, "Provincia guardada."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_provincia(self, id_prov):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM PROVINCIAS WHERE id_provincia=?", (id_prov,))
            conn.commit()
            return True, "Provincia eliminada."
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()

    # --- GENERO ---
    def get_generos(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_Genero, Genero FROM GENERO"
        if search:
            sql += f" WHERE Genero LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_genero(self, id_gen, nombre):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_gen:
                cursor.execute("UPDATE GENERO SET Genero=? WHERE ID_Genero=?", (nombre, id_gen))
            else:
                cursor.execute("SELECT ISNULL(MAX(ID_Genero),0) + 1 FROM GENERO")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO GENERO (ID_Genero, Genero) VALUES (?,?)", (new_id, nombre))
            conn.commit()
            return True, "Género guardado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_genero(self, id_gen):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM GENERO WHERE ID_Genero=?", (id_gen,))
            conn.commit()
            return True, "Género eliminado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # --- CONDICION PAGO ---
    def get_condiciones(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_CONDICION, NOMBRE_CONDICION, ES_CREDITO FROM CONDICION_PAGO"
        if search:
            sql += f" WHERE NOMBRE_CONDICION LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_condicion(self, id_con, nombre, es_credito):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_con:
                cursor.execute("UPDATE CONDICION_PAGO SET NOMBRE_CONDICION=?, ES_CREDITO=? WHERE ID_CONDICION=?", (nombre, es_credito, id_con))
            else:
                cursor.execute("SELECT ISNULL(MAX(ID_CONDICION),0) + 1 FROM CONDICION_PAGO")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO CONDICION_PAGO (ID_CONDICION, NOMBRE_CONDICION, ES_CREDITO) VALUES (?,?,?)", (new_id, nombre, es_credito))
            conn.commit()
            return True, "Condición guardada."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_condicion(self, id_con):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM CONDICION_PAGO WHERE ID_CONDICION=?", (id_con,))
            conn.commit()
            return True, "Condición eliminada."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # --- METODO PAGO ---
    def get_metodos_pago(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_METODO, METODO FROM METODO_PAGO"
        if search:
            sql += f" WHERE METODO LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_metodo_pago(self, id_met, nombre):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_met:
                cursor.execute("UPDATE METODO_PAGO SET METODO=? WHERE ID_METODO=?", (nombre, id_met))
            else:
                cursor.execute("SELECT ISNULL(MAX(ID_METODO),0) + 1 FROM METODO_PAGO")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO METODO_PAGO (ID_METODO, METODO) VALUES (?,?)", (new_id, nombre))
            conn.commit()
            return True, "Método de pago guardado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_metodo_pago(self, id_met):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM METODO_PAGO WHERE ID_METODO=?", (id_met,))
            conn.commit()
            return True, "Método eliminado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # --- METODO ENTREGA ---
    def get_metodos_entrega(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_ENTREGA, TIPO_ENTREGA, ES_ONLINE FROM METODO_ENTREGA"
        if search:
            sql += f" WHERE TIPO_ENTREGA LIKE '%{search}%'"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        return res

    def save_metodo_entrega(self, id_ent, nombre, es_online):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            if id_ent:
                cursor.execute("UPDATE METODO_ENTREGA SET TIPO_ENTREGA=?, ES_ONLINE=? WHERE ID_ENTREGA=?", (nombre, es_online, id_ent))
            else:
                cursor.execute("SELECT ISNULL(MAX(ID_ENTREGA),0) + 1 FROM METODO_ENTREGA")
                new_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO METODO_ENTREGA (ID_ENTREGA, TIPO_ENTREGA, ES_ONLINE) VALUES (?,?,?)", (new_id, nombre, es_online))
            conn.commit()
            return True, "Método de entrega guardado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_metodo_entrega(self, id_ent):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM METODO_ENTREGA WHERE ID_ENTREGA=?", (id_ent,))
            conn.commit()
            return True, "Método eliminado."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
