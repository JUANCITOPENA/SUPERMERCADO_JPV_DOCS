import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.controllers.credit_note_controller import CreditNoteController
from src.config.database import db

class TestCreditNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctrl = CreditNoteController()
        # Buscar una factura real para pruebas
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 NCF_GENERADO FROM VENTAS WHERE ESTADO = 'COMPLETADA'")
        row = cursor.fetchone()
        cls.test_ncf = row[0] if row else None
        conn.close()

    def test_01_search_valid_invoice(self):
        """REQ: Buscar factura existente y traer detalles."""
        if not self.test_ncf:
            self.skipTest("No hay facturas completadas en la BD para probar.")
        
        data, error = self.ctrl.get_invoice_details(self.test_ncf)
        self.assertIsNone(error)
        self.assertIsNotNone(data)
        self.assertEqual(data['ncf'], self.test_ncf)
        self.assertTrue(len(data['items']) > 0)
        print(f"✅ Búsqueda validada para {self.test_ncf}")

    def test_02_search_invalid_invoice(self):
        """REQ: Manejo de errores explícito para facturas inexistentes."""
        data, error = self.ctrl.get_invoice_details("NCF-FANTASMA-999")
        self.assertIsNotNone(error)
        self.assertIn("no encontrada", error)
        print("✅ Manejo de factura inexistente validado.")

    def test_03_ncf_generation(self):
        """REQ: Generación automática de NCF tipo B04."""
        ncf, seq = self.ctrl.generate_next_ncf_b04()
        self.assertTrue(ncf.startswith("B04"))
        self.assertEqual(len(ncf), 11)
        print(f"✅ Generación de NCF validada: {ncf}")

    def test_04_full_credit_note_process(self):
        """REQ: Proceso completo: NC, Stock, Estado Factura."""
        if not self.test_ncf:
            self.skipTest("Sin factura para proceso completo.")

        # 1. Datos iniciales
        data, _ = self.ctrl.get_invoice_details(self.test_ncf)
        item = data['items'][0]
        prod_id = item['id_producto']
        
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT STOCK FROM PRODUCTO WHERE ID_PRODUCTO = ?", (prod_id,))
        stock_inicial = int(cursor.fetchone()[0])

        # 2. Crear NC (Devolución de 1 unidad)
        nc_payload = {
            "ncf_afectado": self.test_ncf,
            "tipo": "DEVOLUCION",
            "usuario": "UnitTester",
            "comentario": "Prueba de cumplimiento técnica",
            "items": [{"id_producto": prod_id, "cantidad": 1, "precio": item['precio']}]
        }
        
        success, msg = self.ctrl.create_credit_note(nc_payload)
        self.assertTrue(success)

        # 3. Validar Stock Incremental
        cursor.execute("SELECT STOCK FROM PRODUCTO WHERE ID_PRODUCTO = ?", (prod_id,))
        stock_final = int(cursor.fetchone()[0])
        self.assertEqual(stock_final, stock_inicial + 1)

        # 4. Validar Estado Factura
        cursor.execute("SELECT ESTADO FROM VENTAS WHERE NCF_GENERADO = ?", (self.test_ncf,))
        nuevo_estado = cursor.fetchone()[0]
        # Como es parcial (1 unidad), debería ser NC_PARCIAL o ANULADA si solo tenía 1
        self.assertIn(nuevo_estado, ['NC_PARCIAL', 'ANULADA'])

        conn.close()
        print(f"✅ Proceso completo validado. Stock: {stock_inicial}->{stock_final}. Estado: {nuevo_estado}")

if __name__ == "__main__":
    unittest.main()
