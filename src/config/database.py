import pyodbc

class DatabaseConnection:
    def __init__(self):
        # Configuración Remota Específica
        self.server = '10.0.0.15'
        self.database = 'SUPERMERCADO_JPV_V6'
        self.username = 'JUANCITO'
        self.password = '123456'
        
        # Connection String estándar para SQL Server Auth
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'TrustServerCertificate=yes;' # Importante para IPs locales/self-signed certs
        )
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            return self.conn
        except pyodbc.Error as ex:
            sqlstate = ex.args[1] if len(ex.args) > 1 else 'No State'
            print(f"❌ Error SQL: {sqlstate} - {ex}")
            raise ex
        except Exception as e:
            print(f"❌ Error General de Conexión: {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

db = DatabaseConnection()
