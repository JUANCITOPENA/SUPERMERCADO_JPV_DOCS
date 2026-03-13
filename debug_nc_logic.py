import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.credit_note_controller import CreditNoteController
from src.config.database import db

def debug_nc():
    print("=== DEBUG NOTAS DE CRÉDITO ===")
    ctrl = CreditNoteController()
    
    # 1. Obtener un NCF real de la base de datos
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 NCF_GENERADO FROM VENTAS WHERE ESTADO IN ('COMPLETADA', 'NC_PARCIAL')")
    row = cursor.fetchone()
    if not row:
        print("❌ No hay facturas elegibles en la BD para probar.")
        conn.close()
        return
    
    real_ncf = row[0]
    print(f"Factura real encontrada: '{real_ncf}'")
    
    # 2. Probar get_invoice_details
    print(f"\nProbando búsqueda de '{real_ncf}'...")
    data, error = ctrl.get_invoice_details(real_ncf)
    
    if error:
        print(f"❌ Error en búsqueda: {error}")
    else:
        print("✅ Búsqueda exitosa!")
        print(f"   ID Venta: {data['id_venta']}")
        print(f"   Items: {len(data['items'])}")
        for item in data['items']:
            print(f"      - {item['producto']}: {item['cantidad_original']} unid.")

    # 3. Probar búsqueda con espacios o minúsculas
    low_ncf = real_ncf.lower()
    print(f"\nProbando búsqueda con minúsculas '{low_ncf}'...")
    data, error = ctrl.get_invoice_details(low_ncf)
    if error:
        print(f"❌ Error en búsqueda minúsculas: {error}")
    else:
        print("✅ Búsqueda minúsculas exitosa!")

    conn.close()

if __name__ == "__main__":
    debug_nc()
