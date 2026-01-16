import unittest
import sys
import os
import importlib

# Agregar root al path
sys.path.append(os.getcwd())

class TestSystemIntegrity(unittest.TestCase):
    def test_imports(self):
        """Prueba que todos los modulos clave se pueden importar (detecta falta de librerias)"""
        modules_to_test = [
            'controllers.auth_controller',
            'controllers.products_controller',
            'controllers.vendor_controller',
            'controllers.sales_controller',
            'utils.helpers', # Aqui fallaba antes por requests
            'views.main_window_ui',
            'views.pos_ui'
        ]
        print("\n🔍 Verificando Importaciones...")
        for mod_name in modules_to_test:
            try:
                importlib.import_module(mod_name)
                print(f"   ✅ Modulo '{mod_name}' OK")
            except ImportError as e:
                self.fail(f"❌ Fallo al importar {mod_name}: {e}")

class TestAuthIntegration(unittest.TestCase):
    def setUp(self):
        from controllers.auth_controller import AuthController
        self.auth = AuthController()
        
    def test_connection(self):
        """Verifica que AuthController puede conectar a la BD"""
        from database import db
        conn = db.connect()
        self.assertIsNotNone(conn, "❌ La conexión a BD devolvió None")
        if conn:
            conn.close()
            print("\n✅ Conexión a BD verificada.")

    def test_login_success(self):
        """Prueba de Login Exitoso (Admin)"""
        print("   🧪 Probando Login Correcto...")
        user = self.auth.login("Juancito", "123456")
        self.assertIsNotNone(user, "El usuario debería existir")
        self.assertEqual(user[0], 1, "El ID de Juancito debe ser 1")
        self.assertEqual(user[1], 'admin', "El Rol de Juancito debe ser admin")
        print("   ✅ Login Admin OK")

    def test_login_fail_password(self):
        """Prueba de Contraseña Incorrecta"""
        print("   🧪 Probando Password Incorrecto...")
        user = self.auth.login("Juancito", "clave_falsa")
        self.assertIsNone(user, "El login debería fallar con clave falsa")
        print("   ✅ Bloqueo por Password OK")

    def test_login_fail_user(self):
        """Prueba de Usuario Inexistente"""
        print("   🧪 Probando Usuario Fantasma...")
        user = self.auth.login("UsuarioInexistenteXYZ", "123456")
        self.assertIsNone(user, "El login debería fallar con usuario inexistente")
        print("   ✅ Bloqueo por Usuario OK")

if __name__ == '__main__':
    print("🚀 INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS (V7)")
    print("================================================")
    unittest.main(verbosity=2)
