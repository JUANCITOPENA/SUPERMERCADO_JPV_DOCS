import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.credit_note_controller import CreditNoteController
from src.config.database import db

def debug_full_failure():
    ctrl = CreditNoteController()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 NCF_GENERADO FROM VENTAS WHERE ESTADO = 'COMPLETADA'")
    ncf = cursor.fetchone()[0]
    conn.close()

    data, _ = ctrl.get_invoice_details(ncf)
    item = data['items'][0]
    
    nc_payload = {
        "ncf_afectado": ncf,
        "tipo": "DEVOLUCION",
        "usuario": "DebugUser",
        "comentario": "Debugging failure",
        "items": [{"id_producto": item['id_producto'], "cantidad": 1, "precio": item['precio']}]
    }
    
    success, msg = ctrl.create_credit_note(nc_payload)
    print(f"Success: {success}")
    print(f"Message: {msg}")

if __name__ == "__main__":
    debug_full_failure()
