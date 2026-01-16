import pyodbc

server = r'(localdb)\MSSQLLocalDB'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=SUPERMERCADO_JPV_V6;Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    print("--- TABLAS ENCONTRADAS ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    for row in cursor.fetchall():
        print(f"- {row[0]}")
        
    print("\n--- VISTAS ENCONTRADAS ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'VIEW'")
    for row in cursor.fetchall():
        print(f"- {row[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
