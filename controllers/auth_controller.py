import hashlib
from database import db

class AuthController:
    def login(self, user, password):
        print(f"--- Intentando Login: {user} ---") # Debug en consola
        conn = db.connect()
        if not conn:
            print("Error: No se pudo conectar a la BD")
            return None
        
        cursor = conn.cursor()
        
        # CORRECCIÓN IMPORTANTE:
        # CAST(? AS VARCHAR(50)) convierte el texto Unicode de Python a ASCII
        # para que coincida con cómo guardamos la clave en el script SQL inicial.
        query = """
            SELECT ID_USUARIO, ROL 
            FROM USUARIOS 
            WHERE NOMBRE_USUARIO = ? 
            AND PASSWORD = HASHBYTES('SHA2_256', CAST(? AS VARCHAR(50)))
        """
        
        try:
            cursor.execute(query, (user, password))
            result = cursor.fetchone()
            
            if result:
                print(f"Login Exitoso. ID: {result[0]}, ROL: {result[1]}")
                return result
            else:
                print("Login Fallido: Usuario o clave no coinciden en BD.")
                return None
                
        except Exception as e:
            print(f"Error crítico en consulta SQL: {e}")
            return None
        finally:
            conn.close()