import unittest
from unittest.mock import MagicMock, patch
from controllers.aux_controller import AuxController

class TestAuxController(unittest.TestCase):
    def setUp(self):
        self.ctrl = AuxController()

    @patch('controllers.aux_controller.db')
    def test_get_regions(self, mock_db):
        # Setup Mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [(1, 'Norte'), (2, 'Sur')]
        
        # Action
        result = self.ctrl.get_regions()
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], 'Norte')
        mock_cursor.execute.assert_called()
        mock_conn.close.assert_called()

    @patch('controllers.aux_controller.db')
    def test_save_region_insert(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = [10] # Max ID
        
        # Save new region (id=None)
        ok, msg = self.ctrl.save_region(None, "Este")
        
        self.assertTrue(ok)
        # Check that we got ID and Inserted
        mock_cursor.execute.assert_any_call("SELECT ISNULL(MAX(ID_REGION),0) + 1 FROM REGION")
        mock_cursor.execute.assert_any_call("INSERT INTO REGION (ID_REGION, REGION) VALUES (?,?)", (10, "Este"))
        mock_conn.commit.assert_called()

    @patch('controllers.aux_controller.db')
    def test_save_region_update(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Update existing
        ok, msg = self.ctrl.save_region(5, "Oeste")
        
        self.assertTrue(ok)
        mock_cursor.execute.assert_called_with("UPDATE REGION SET REGION=? WHERE ID_REGION=?", ("Oeste", 5))
        mock_conn.commit.assert_called()

    @patch('controllers.aux_controller.db')
    def test_delete_region(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        ok, msg = self.ctrl.delete_region(5)
        
        self.assertTrue(ok)
        mock_cursor.execute.assert_called_with("DELETE FROM REGION WHERE ID_REGION=?", (5,))
        mock_conn.commit.assert_called()

    @patch('controllers.aux_controller.db')
    def test_get_provincias(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [(1, 'Santiago', 'Cibao', 2)]
        
        result = self.ctrl.get_provincias("Sant")
        
        self.assertEqual(len(result), 1)
        self.assertIn("WHERE P.nombreProvincia LIKE '%Sant%'", mock_cursor.execute.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
