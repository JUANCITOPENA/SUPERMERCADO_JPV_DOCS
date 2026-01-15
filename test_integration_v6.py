import sys
import os

# Asegurar que encuentre los módulos
sys.path.append(os.getcwd())

from database import db
from controllers.products_controller import ProductController
from controllers.client_controller import ClientController
from controllers.sales_controller import SalesController

def run_test():
    print("=== INICIANDO TEST DE INTEGRACIÓN MINI ERP V6 ===")
    
    # 1. Prueba de Conexión
    print("\n[1] Probando Conexión a SQL Server...")
    conn = db.connect()
    if conn:
        print("   ✅ Conexión Exitosa.")
        conn.close()
    else:
        print("   ❌ Error de Conexión. Revisa database.py")
        sys.exit(1)

    # 2. Prueba de Productos
    print("\n[2] Test ProductController...")
    try:
        pc = ProductController()
        prods = pc.get_all_products()
        print(f"   ✅ Productos obtenidos: {len(prods)}")
        if len(prods) > 0:
            print(f"   ℹ️ Ejemplo: {prods[0]}")
    except Exception as e:
        print(f"   ❌ Error en Productos: {e}")

    # 3. Prueba de Clientes
    print("\n[3] Test ClientController...")
    try:
        cc = ClientController()
        clients = cc.get_all_clients()
        print(f"   ✅ Clientes obtenidos: {len(clients)}")
    except Exception as e:
        print(f"   ❌ Error en Clientes: {e}")

    # 4. Prueba de Ventas (Lectura)
    print("\n[4] Test SalesController (Datos Maestros)...")
    try:
        sc = SalesController()
        clients_combo = sc.get_clients()
        products_combo = sc.get_products()
        print(f"   ✅ Datos para Combo Clientes: {len(clients_combo)}")
        print(f"   ✅ Datos para Combo Productos: {len(products_combo)}")
    except Exception as e:
        print(f"   ❌ Error en Ventas: {e}")
        
    print("\n=== TEST FINALIZADO ===")

if __name__ == "__main__":
    run_test()
