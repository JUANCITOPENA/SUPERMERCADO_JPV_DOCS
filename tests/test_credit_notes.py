import unittest
from src.controllers.credit_note_controller import CreditNoteController
from src.config.database import db

class TestCreditNotes(unittest.TestCase):
    def setUp(self):
        self.controller = CreditNoteController()
        # Ensure we have at least one valid invoice to test
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 ID_VENTA, NCF_GENERADO, TOTAL_VENTA FROM VENTAS WHERE ESTADO = 'COMPLETADA'")
        self.test_invoice = cursor.fetchone()
        conn.close()

    def test_search_invoices(self):
        """Prueba que la busqueda de facturas devuelva resultados."""
        res = self.controller.search_invoices()
        self.assertIsInstance(res, list)
        if self.test_invoice:
            self.assertTrue(len(res) > 0)

    def test_get_invoice_details(self):
        """Prueba la obtencion de detalles de una factura."""
        if not self.test_invoice: self.skipTest("No hay facturas para probar")
        data, err = self.controller.get_invoice_details(self.test_invoice[0])
        self.assertIsNone(err)
        self.assertEqual(data['ncf'], self.test_invoice[1])
        self.assertTrue(len(data['items']) > 0)

    def test_create_credit_note_logic(self):
        """Simula la creacion de una nota de credito."""
        if not self.test_invoice: self.skipTest("No hay facturas para probar")
        
        # Obtener detalles reales para el payload
        details, _ = self.controller.get_invoice_details(self.test_invoice[0])
        
        # Devolver solo 1 unidad del primer item
        it = details['items'][0]
        it['qty_refund'] = 1
        
        payload = {
            "id_venta": details['id_venta'],
            "total_venta": details['total'],
            "usuario": "TestUnit",
            "motivo": "Prueba Unitaria",
            "items": [it]
        }
        
        ok, msg = self.controller.create_credit_note(payload)
        self.assertTrue(ok)
        self.assertIn("generada con exito", msg)

if __name__ == '__main__':
    unittest.main()
