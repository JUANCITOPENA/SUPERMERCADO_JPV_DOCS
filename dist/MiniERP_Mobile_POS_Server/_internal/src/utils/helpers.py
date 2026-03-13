import requests
from src.config.database import db

def get_next_id(table_name, id_column):
    """Calcula el siguiente ID (Max + 1) para cualquier tabla."""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT ISNULL(MAX({id_column}), 0) + 1 FROM {table_name}")
        next_id = cursor.fetchone()[0]
        conn.close()
        return next_id
    except Exception as e:
        print(f"Error obteniendo ID: {e}")
        return 1
