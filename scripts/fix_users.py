import pyodbc

server = r'(localdb)\MSSQLLocalDB'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=SUPERMERCADO_JPV_V6;Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    # 1. Limpiar usuario si existe (para evitar duplicados o estados incorrectos)
    cursor.execute("DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = 'Juancito'")
    
    # 2. Insertar Usuario Juancito
    # IMPORTANTE: Usamos CAST('123456' AS VARCHAR(50)) para asegurar que el hash coincida
    # con lo que espera el controlador (que hace lo mismo).
    sql = """
    INSERT INTO USUARIOS (ID_USUARIO, NOMBRE_USUARIO, PASSWORD, ROL, ID_REGION)
    VALUES (
        1, 
        'Juancito', 
        HASHBYTES('SHA2_256', CAST('123456' AS VARCHAR(50))), 
        'admin', 
        NULL
    )
    """
    cursor.execute(sql)
    
    print("✅ Usuario 'Juancito' creado/restaurado correctamente.")
    print("   Contraseña: '123456'")
    
    # Verificación
    cursor.execute("SELECT ID_USUARIO, NOMBRE_USUARIO FROM USUARIOS WHERE NOMBRE_USUARIO='Juancito'")
    row = cursor.fetchone()
    if row:
        print(f"   Verificado en BD: {row}")
    
    conn.close()

except Exception as e:
    print(f"❌ Error al crear usuario: {e}")
