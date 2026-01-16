
from src.config.database import db
class AuthController:
    def login(self, user, pwd):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_USUARIO, ROL FROM USUARIOS WHERE NOMBRE_USUARIO=? AND PASSWORD=HASHBYTES('SHA2_256', CAST(? AS VARCHAR(50)))", (user, pwd))
        res = cursor.fetchone()
        conn.close()
        return res
