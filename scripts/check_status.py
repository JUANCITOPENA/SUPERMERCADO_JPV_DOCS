import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config.database import db

try:
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ESTADO FROM VENTAS")
    print(f"ESTADOS ENCONTRADOS: {[row[0] for row in cursor.fetchall()]}")
    conn.close()
except Exception as e:
    print(e)
