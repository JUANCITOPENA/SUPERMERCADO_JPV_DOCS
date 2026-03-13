import pyodbc
from src.config.settings import ConfigManager

class DatabaseConnection:
    def __init__(self):
        # Cargar configuración inicial
        config = ConfigManager.load_config()
        
        self.server = config.get('server_ip', '10.0.0.15')
        self.database = 'SUPERMERCADO_JPV_V6'
        self.username = 'JUANCITO'
        self.password = '123456'
        self.conn = None

    def get_connection_string(self):
        # Recargar config por si cambió en tiempo de ejecución
        config = ConfigManager.load_config()
        self.server = config.get('server_ip', self.server)
        
        return (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'TrustServerCertificate=yes;'
        )

    def connect(self):
        try:
            conn_str = self.get_connection_string()
            self.conn = pyodbc.connect(conn_str)
            return self.conn
        except pyodbc.Error as ex:
            sqlstate = ex.args[1] if len(ex.args) > 1 else 'No State'
            print(f"❌ Error SQL ({self.server}): {sqlstate} - {ex}")
            raise ex
        except Exception as e:
            print(f"❌ Error General ({self.server}): {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

db = DatabaseConnection()
