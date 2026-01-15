import pyodbc
import random
from datetime import datetime, timedelta

server = r'(localdb)\MSSQLLocalDB'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=SUPERMERCADO_JPV_V6;Trusted_Connection=yes;'

def populate():
    print("🚀 Iniciando Poblado Masivo de Datos...")
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        # 1. Limpiar datos viejos (opcional, para evitar dupes)
        print("   - Limpiando tablas de movimiento...")
        cursor.execute("DELETE FROM DETALLE_VENTAS")
        cursor.execute("DELETE FROM VENTAS")
        cursor.execute("DELETE FROM PRODUCTO")
        cursor.execute("DELETE FROM CLIENTE WHERE ID_CLIENTE > 1") 

        # 2. Insertar Productos (50 items)
        print("   - Insertando 50 Productos...")
        nombres = ['Arroz', 'Habichuelas', 'Aceite', 'Leche', 'Pan', 'Queso', 'Salami', 'Pollo', 'Res', 'Chuleta', 'Pasta', 'Salsa', 'Sazon', 'Jabon', 'Shampoo', 'Papel', 'Refresco', 'Agua', 'Cerveza', 'Ron']
        marcas = ['Rica', 'Campo', 'Crisol', 'Milex', 'Bimbo', 'Sosua', 'Induveca', 'Cibao', 'Norte', 'Don Pedro', 'Milano', 'Goya', 'Maggi', 'Candado', 'Head&S', 'Suave', 'CocaCola', 'Dasani', 'Presidente', 'Brugal']
        
        for i in range(1, 51):
            nom = f"{random.choice(nombres)} {random.choice(marcas)}"
            stock = random.randint(5, 200)
            costo = random.randint(50, 500)
            precio = int(costo * 1.30)
            cursor.execute("INSERT INTO PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA, GRAVADO_ITBIS) VALUES (?, ?, ?, ?, ?, 1)", (i, nom, stock, costo, precio))

        # 3. Insertar Clientes (20 personas)
        print("   - Insertando 20 Clientes...")
        nombres_cli = ['Jose', 'Maria', 'Pedro', 'Ana', 'Luis', 'Carmen', 'Carlos', 'Rosa', 'Miguel', 'Elena']
        apellidos_cli = ['Perez', 'Garcia', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Diaz', 'Sanchez', 'Ramirez']
        
        for i in range(2, 22): # Empezamos en 2 porque el 1 ya existe
            nom = random.choice(nombres_cli)
            ape = random.choice(apellidos_cli)
            rnc = f"001{random.randint(10000000, 99999999)}"
            cursor.execute("EXEC SP_CREAR_CLIENTE ?, ?, ?, 'FISICA', 1, 1, 'Calle Falsa 123', 0, 0", (nom, ape, rnc))

        # 4. Generar Ventas Históricas (Para Reportes)
        print("   - Generando 30 Ventas Históricas...")
        for i in range(30):
            id_cli = random.randint(1, 20)
            id_prod = random.randint(1, 50)
            cant = random.randint(1, 10)
            # Usamos el SP
            try:
                cursor.execute("EXEC SP_FACTURAR_VENTA ?, 1, ?, ?, 1, 1", (id_cli, id_prod, cant))
            except:
                pass # Ignorar errores de stock randoms

        print("✅ Base de Datos Poblada Exitosamente.")
        conn.close()
    except Exception as e:
        print(f"❌ Error poblando datos: {e}")

if __name__ == "__main__":
    populate()
