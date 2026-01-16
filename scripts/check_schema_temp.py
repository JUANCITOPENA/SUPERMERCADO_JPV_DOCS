import sys
import os

# Fix path to find src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

try:
    conn = db.connect()
    cursor = conn.cursor()
    
    # 1. Listar Tablas
    print("--- TABLAS ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
    tables = [row[0] for row in cursor.fetchall()]
    print(tables)
    
    # 2. Verificar Columnas de PRODUCTOS
    prod_table = next((t for t in tables if 'PROD' in t.upper()), None)
    if prod_table:
        print(f"\n--- COLUMNAS DE {prod_table} ---")
        cursor.execute(f"SELECT TOP 1 * FROM {prod_table}")
        print([d[0] for d in cursor.description])

    conn.close()
except Exception as e:
    print(f"Error: {e}")