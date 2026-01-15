from database import db
import pyodbc

class ClientController:
    def get_all_clients(self, search_term=""):
        conn = db.connect()
        if not conn: return []
        cursor = conn.cursor()
        query = """
        SELECT c.ID_CLIENTE, c.NOMBRE_CLIENTE, c.APELLIDO_CLIENTE, c.RNC_CEDULA, c.TIPO_PERSONA, 
               r.REGION, p.nombreProvincia
        FROM CLIENTE c
        JOIN REGION r ON c.id_region = r.ID_REGION
        LEFT JOIN PROVINCIAS p ON c.id_provincia = p.id_provincia
        """
        if search_term:
            query += " WHERE c.NOMBRE_CLIENTE LIKE ? OR c.APELLIDO_CLIENTE LIKE ? OR c.RNC_CEDULA LIKE ?"
            params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        clients = cursor.fetchall()
        conn.close()
        return clients

    def create_client(self, nombre, apellido, rnc, tipo, region_id, prov_id, direccion, credito, limite):
        conn = db.connect()
        if not conn: return False, "No connection"
        cursor = conn.cursor()
        try:
            # Using the stored procedure as requested
            sql = """
            EXEC SP_CREAR_CLIENTE 
                @Nombre = ?, @Apellido = ?, @RNC_Cedula = ?, 
                @TipoPersona = ?, @Region = ?, @Provincia = ?, 
                @Direccion = ?, @TieneCredito = ?, @LimiteCredito = ?
            """
            cursor.execute(sql, (nombre, apellido, rnc, tipo, region_id, prov_id, direccion, credito, limite))
            conn.commit()
            return True, "Cliente creado exitosamente."
        except pyodbc.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def update_client(self, id_cliente, direccion, limite):
        conn = db.connect()
        if not conn: return False, "No connection"
        cursor = conn.cursor()
        try:
            # Using the stored procedure as requested
            sql = "EXEC SP_ACTUALIZAR_CLIENTE @ID_Cliente = ?, @Direccion = ?, @LimiteCredito = ?"
            cursor.execute(sql, (id_cliente, direccion, limite))
            conn.commit()
            return True, "Cliente actualizado."
        except pyodbc.Error as e:
            return False, str(e)
        finally:
            conn.close()
            
    def get_regions(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_REGION, REGION FROM REGION")
        data = cursor.fetchall()
        conn.close()
        return data

    def get_provinces_by_region(self, region_id):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id_provincia, nombreProvincia FROM PROVINCIAS WHERE id_region = ?", (region_id,))
        data = cursor.fetchall()
        conn.close()
        return data
