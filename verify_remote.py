
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    from database import db
    print(f"🔄 Intentando conectar a {db.server}...")
    conn = db.connect()
    cursor = conn.cursor()
    
    print("✅ Conexión Exitosa.")
    
    # Validar Datos
    cursor.execute("SELECT COUNT(*) FROM PRODUCTO")
    prod_count = cursor.fetchone()[0]
    print(f"📦 Productos encontrados: {prod_count}")
    
    cursor.execute("SELECT COUNT(*) FROM VENTAS")
    sales_count = cursor.fetchone()[0]
    print(f"💰 Ventas encontradas: {sales_count}")
    
    conn.close()
except Exception as e:
    print(f"❌ FALLÓ LA CONEXIÓN: {e}")
