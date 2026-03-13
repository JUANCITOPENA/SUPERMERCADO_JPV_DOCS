import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.credit_note_controller import CreditNoteController

def test_search():
    ctrl = CreditNoteController()
    ncf = "E320001000000"
    print(f"--- Probando búsqueda de factura: {ncf} ---")
    data, error = ctrl.get_invoice_details(ncf)
    
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Factura encontrada!")
        print(f"   ID: {data['id_venta']}")
        print(f"   Total: {data['total']}")
        print(f"   Items: {len(data['items'])}")
        for item in data['items']:
            print(f"      - {item['producto']} (Cant: {item['cantidad_original']})")

if __name__ == "__main__":
    test_search()
