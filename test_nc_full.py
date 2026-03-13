import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.credit_note_controller import CreditNoteController

def test_full_process():
    ctrl = CreditNoteController()
    ncf_target = "E320001000000" # Ya sabemos que existe
    
    print(f"--- Iniciando Test de Creación de NC para: {ncf_target} ---")
    
    # 1. Obtener detalles
    data, error = ctrl.get_invoice_details(ncf_target)
    if error:
        print(f"❌ Error al buscar: {error}")
        return

    # 2. Simular devolución parcial del primer item
    item = data['items'][0]
    nc_data = {
        "ncf_afectado": ncf_target,
        "tipo": "DEVOLUCION",
        "usuario": "TestUser",
        "comentario": "Test de devolución automatizada",
        "items": [
            {"id_producto": item['id_producto'], "cantidad": 1, "precio": item['precio']}
        ]
    }
    
    # 3. Procesar NC
    success, msg = ctrl.create_credit_note(nc_data)
    if success:
        print(f"✅ {msg}")
    else:
        print(f"❌ Error al crear NC: {msg}")

if __name__ == "__main__":
    test_full_process()
