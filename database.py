import pyodbc
from PyQt6.QtWidgets import QMessageBox

class DatabaseConnection:
    def __init__(self):
        self.server = r'(localdb)\MSSQLLocalDB'
        self.database = 'SUPERMERCADO_JPV_V6'
        # Usamos Trusted Connection para LocalDB (Windows Auth)
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'Trusted_Connection=yes;'
        )
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            return self.conn
        except Exception as e:
            print(f"Error de conexión: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()

# Instancia global para usar en todo el proyecto
db = DatabaseConnection()