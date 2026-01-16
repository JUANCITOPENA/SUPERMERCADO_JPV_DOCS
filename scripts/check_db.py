import pyodbc

server = r'(localdb)\MSSQLLocalDB'
database = 'SUPERMERCADO_JPV_V6'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    tables = ['CLIENTE', 'PRODUCTO', 'VENDEDOR', 'VENTAS', 'USUARIOS']
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            print(f"Table {t}: {count} rows")
        except Exception as e:
            print(f"Table {t}: Error - {e}")

    # Check Columns for CLIENTE
    print("\nColumns in CLIENTE:")
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CLIENTE'")
    for row in cursor.fetchall():
        print(f" - {row[0]}")

    conn.close()
except Exception as e:
    print(f"Connection Error: {e}")

