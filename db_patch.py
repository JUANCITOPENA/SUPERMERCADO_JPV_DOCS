import pyodbc

server = r'(localdb)\MSSQLLocalDB'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=SUPERMERCADO_JPV_V6;Trusted_Connection=yes;'

sql_commands = [
    # Tablas Faltantes
    "IF OBJECT_ID('TIPO_NCF') IS NULL CREATE TABLE TIPO_NCF (ID_TIPO_NCF INT PRIMARY KEY, SERIE_NCF VARCHAR(3), DESCRIPCION VARCHAR(100))",
    "IF OBJECT_ID('CONDICION_PAGO') IS NULL CREATE TABLE CONDICION_PAGO (ID_CONDICION INT PRIMARY KEY, NOMBRE_CONDICION VARCHAR(50), ES_CREDITO BIT)",
    "IF OBJECT_ID('METODO_PAGO') IS NULL CREATE TABLE METODO_PAGO (ID_METODO INT PRIMARY KEY, METODO VARCHAR(50))",
    "IF OBJECT_ID('METODO_ENTREGA') IS NULL CREATE TABLE METODO_ENTREGA (ID_ENTREGA INT PRIMARY KEY, TIPO_ENTREGA VARCHAR(50))",
    """IF OBJECT_ID('VENTAS') IS NULL CREATE TABLE VENTAS (
        ID_VENTA INT PRIMARY KEY IDENTITY(1,1), FECHA DATETIME, ID_CLIENTE INT, ID_VENDEDOR INT, 
        ID_REGION INT, ID_CONDICION INT, ID_METODO_PAGO INT, ID_ENTREGA INT, ID_TIPO_NCF INT, 
        NCF_GENERADO VARCHAR(20), SUBTOTAL_VENTA DECIMAL(12,2), TOTAL_ITBIS DECIMAL(12,2), TOTAL_VENTA DECIMAL(12,2), ESTADO VARCHAR(20)
    )""",
    """IF OBJECT_ID('DETALLE_VENTAS') IS NULL CREATE TABLE DETALLE_VENTAS (
        ID_DETALLE INT PRIMARY KEY IDENTITY(1,1), ID_VENTA INT, ID_PRODUCTO INT, 
        CANTIDAD INT, PRECIO_UNITARIO DECIMAL(9,2), ITBIS_UNITARIO DECIMAL(9,2), SUBTOTAL DECIMAL(12,2)
    )""",
    
    # Datos Maestros
    "IF NOT EXISTS (SELECT * FROM TIPO_NCF) INSERT INTO TIPO_NCF VALUES (1, 'E31', 'Credito Fiscal'), (2, 'E32', 'Consumo')",
    "IF NOT EXISTS (SELECT * FROM METODO_PAGO) INSERT INTO METODO_PAGO VALUES (1, 'Efectivo'), (2, 'Tarjeta'), (3, 'Transferencia'), (4, 'Cheque')",
    "IF NOT EXISTS (SELECT * FROM METODO_ENTREGA) INSERT INTO METODO_ENTREGA VALUES (1, 'Tienda'), (2, 'Delivery'), (3, 'Envio')",
    "IF NOT EXISTS (SELECT * FROM CONDICION_PAGO) INSERT INTO CONDICION_PAGO VALUES (1, 'Contado', 0), (2, 'Credito', 1)",
    
    # Procedimientos Almacenados
    """
    CREATE OR ALTER PROCEDURE SP_FACTURAR_VENTA
        @ID_Cliente INT, @ID_Vendedor INT, @ID_Producto INT, @Cantidad INT, @ID_MetodoPago INT, @ID_Entrega INT
    AS
    BEGIN
        SET NOCOUNT ON;
        DECLARE @Precio DECIMAL(9,2), @Total DECIMAL(12,2);
        
        -- Validar Stock
        IF (SELECT STOCK FROM PRODUCTO WHERE ID_PRODUCTO = @ID_Producto) < @Cantidad
        BEGIN
            RAISERROR('Stock insuficiente', 16, 1);
            RETURN;
        END

        SELECT @Precio = PRECIO_VENTA FROM PRODUCTO WHERE ID_PRODUCTO = @ID_Producto;
        
        -- Insertar Venta
        INSERT INTO VENTAS (FECHA, ID_CLIENTE, ID_VENDEDOR, ID_REGION, ID_CONDICION, ID_METODO_PAGO, ID_ENTREGA, ID_TIPO_NCF, NCF_GENERADO, TOTAL_VENTA)
        VALUES (GETDATE(), @ID_Cliente, @ID_Vendedor, 1, 1, @ID_MetodoPago, @ID_Entrega, 2, 'E320000001', (@Precio * @Cantidad));
        
        DECLARE @ID_Venta INT = SCOPE_IDENTITY();
        
        -- Insertar Detalle
        INSERT INTO DETALLE_VENTAS (ID_VENTA, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO, SUBTOTAL)
        VALUES (@ID_Venta, @ID_Producto, @Cantidad, @Precio, (@Precio * @Cantidad));
        
        -- Descontar Stock
        UPDATE PRODUCTO SET STOCK = STOCK - @Cantidad WHERE ID_PRODUCTO = @ID_Producto;
    END
    """,
    """
    CREATE OR ALTER PROCEDURE SP_CREAR_CLIENTE
        @Nombre VARCHAR(100), @Apellido VARCHAR(100), @RNC_Cedula VARCHAR(20), 
        @TipoPersona VARCHAR(20), @Region INT, @Provincia INT, 
        @Direccion VARCHAR(200), @TieneCredito BIT, @LimiteCredito DECIMAL(12,2)
    AS
    BEGIN
        INSERT INTO CLIENTE (ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, RNC_CEDULA, TIPO_PERSONA, id_region, id_provincia, DIRECCION, TIENE_CREDITO_APROBADO, LIMITE_CREDITO)
        VALUES ((SELECT ISNULL(MAX(ID_CLIENTE),0)+1 FROM CLIENTE), @Nombre, @Apellido, @RNC_Cedula, @TipoPersona, @Region, @Provincia, @Direccion, @TieneCredito, @LimiteCredito);
    END
    """,
    """
    CREATE OR ALTER PROCEDURE SP_ACTUALIZAR_CLIENTE
        @ID_Cliente INT, @Direccion VARCHAR(200), @LimiteCredito DECIMAL(12,2)
    AS
    BEGIN
        UPDATE CLIENTE SET DIRECCION=@Direccion, LIMITE_CREDITO=@LimiteCredito WHERE ID_CLIENTE=@ID_Cliente;
    END
    """
]

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    for sql in sql_commands:
        cursor.execute(sql)
    print("✅ BD Parcheada Exitosamente: Tablas y Procedimientos creados.")
except Exception as e:
    print(f"Error: {e}")
