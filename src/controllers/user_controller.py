
from src.config.database import db

class UserController:
    def get_all(self, search=""):
        conn = db.connect()
        cursor = conn.cursor()
        sql = "SELECT ID_USUARIO, NOMBRE_USUARIO, ROL, ID_REGION FROM USUARIOS"
        if search:
            sql += f" WHERE NOMBRE_USUARIO LIKE '%{search}%'"
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return data

    def save(self, id_u, user, pwd, rol, region_id):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # Hash password logic is handled by DB function HASHBYTES in Insert/Update
            # Check if exists
            if id_u:
                # Update
                # Only update password if provided (not empty)
                if pwd:
                    sql = "UPDATE USUARIOS SET NOMBRE_USUARIO=?, PASSWORD=HASHBYTES('SHA2_256', CAST(? AS VARCHAR(50))), ROL=?, ID_REGION=? WHERE ID_USUARIO=?"
                    cursor.execute(sql, (user, pwd, rol, region_id, id_u))
                else:
                    sql = "UPDATE USUARIOS SET NOMBRE_USUARIO=?, ROL=?, ID_REGION=? WHERE ID_USUARIO=?"
                    cursor.execute(sql, (user, rol, region_id, id_u))
            else:
                # Insert
                cursor.execute("SELECT ISNULL(MAX(ID_USUARIO), 0) + 1 FROM USUARIOS")
                new_id = cursor.fetchone()[0]
                sql = "INSERT INTO USUARIOS (ID_USUARIO, NOMBRE_USUARIO, PASSWORD, ROL, ID_REGION) VALUES (?, ?, HASHBYTES('SHA2_256', CAST(? AS VARCHAR(50))), ?, ?)"
                cursor.execute(sql, (new_id, user, pwd, rol, region_id))
            
            conn.commit()
            return True, "Usuario guardado exitosamente"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete(self, id_u):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # Prevent deleting admin default
            if id_u == 1:
                return False, "No se puede eliminar el super-admin."
            cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO=?", (id_u,))
            conn.commit()
            return True, "Usuario eliminado"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
