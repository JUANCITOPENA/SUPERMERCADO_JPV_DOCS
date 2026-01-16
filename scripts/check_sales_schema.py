import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

try:
    conn = db.connect()
    cursor = conn.cursor()
    
    print("--- COLUMNAS DE VENTAS ---")
    cursor.execute("SELECT TOP 1 * FROM VENTAS")
    print([d[0] for d in cursor.description])

    conn.close()
except Exception as e:
    print(f"Error: {e}")
