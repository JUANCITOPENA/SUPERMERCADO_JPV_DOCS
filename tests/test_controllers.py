
import unittest
from controllers.client_controller import ClientController
from controllers.products_controller import ProductController
from controllers.vendor_controller import VendorController
from controllers.sales_controller import SalesController
from database import db

class TestControllers(unittest.TestCase):
    def setUp(self):
        # Ensure connection works
        self.conn = db.connect()
        self.assertIsNotNone(self.conn)
        self.conn.close()

    def test_get_clients(self):
        c = ClientController()
        data = c.get_all()
        self.assertIsInstance(data, list)
        # Assuming DB has data as per check_db.py
        if data:
            self.assertEqual(len(data[0]), 12) # 12 columns

    def test_get_products(self):
        c = ProductController()
        data = c.get_all()
        self.assertIsInstance(data, list)
        if data:
            self.assertEqual(len(data[0]), 6)

    def test_get_vendors(self):
        c = VendorController()
        data = c.get_all()
        self.assertIsInstance(data, list)

    def test_sales_config(self):
        c = SalesController()
        pay = c.get_payment_methods()
        deli = c.get_delivery_methods()
        self.assertTrue(len(pay) > 0)
        self.assertTrue(len(deli) > 0)

if __name__ == '__main__':
    unittest.main()
