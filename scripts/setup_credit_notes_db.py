import sys
import os
import pyodbc

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

def setup_credit_notes():
    print("--- Configurando Tablas para Notas de Crédito (MiniERP V9) ---")
    
    conn = db.connect()
    if not conn:
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()

        # 1. Tabla Encabezado: NOTAS_CREDITO
        sql_header = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='NOTAS_CREDITO' AND xtype='U')
        BEGIN
            CREATE TABLE NOTAS_CREDITO (
                ID_Nota INT IDENTITY(1,1) PRIMARY KEY,
                NCF_Nota VARCHAR(20) NOT NULL UNIQUE,
                NCF_Afectado VARCHAR(20) NOT NULL,
                Tipo VARCHAR(50) NOT NULL, -- 'ANULACION', 'DEVOLUCION'
                Monto_Total DECIMAL(18,2) DEFAULT 0,
                Fecha DATETIME DEFAULT GETDATE(),
                Estado VARCHAR(20) DEFAULT 'ACTIVA', -- 'ACTIVA', 'ANULADA'
                Usuario_Creador VARCHAR(50),
                Comentario VARCHAR(255)
            );
            PRINT '✅ Tabla NOTAS_CREDITO creada.';
        END
        ELSE
        BEGIN
            PRINT 'ℹ️ Tabla NOTAS_CREDITO ya existe.';
        END
        """
        cursor.execute(sql_header)

        # 2. Tabla Detalle: DETALLE_NOTA_CREDITO
        sql_detail = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='DETALLE_NOTA_CREDITO' AND xtype='U')
        BEGIN
            CREATE TABLE DETALLE_NOTA_CREDITO (
                ID_Detalle INT IDENTITY(1,1) PRIMARY KEY,
                ID_Nota INT NOT NULL,
                ID_Producto INT NOT NULL,
                Cantidad INT NOT NULL,
                Precio_Unitario DECIMAL(18,2) NOT NULL,
                Subtotal DECIMAL(18,2) NOT NULL,
                FOREIGN KEY (ID_Nota) REFERENCES NOTAS_CREDITO(ID_Nota),
                FOREIGN KEY (ID_Producto) REFERENCES PRODUCTO(ID_Producto)
            );
            PRINT '✅ Tabla DETALLE_NOTA_CREDITO creada.';
        END
        ELSE
        BEGIN
            PRINT 'ℹ️ Tabla DETALLE_NOTA_CREDITO ya existe.';
        END
        """
        cursor.execute(sql_detail)

        # 3. Secuencia para NCF B04 (Si no existe una tabla de secuencias, la creamos o usamos una lógica simple)
        # Para este ejemplo, usaremos una tabla de configuración de secuencias si no existe
        sql_sequence_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SECUENCIAS_NCF' AND xtype='U')
        BEGIN
            CREATE TABLE SECUENCIAS_NCF (
                Tipo VARCHAR(5) PRIMARY KEY,
                Ultimo_Numero INT DEFAULT 0
            );
            INSERT INTO SECUENCIAS_NCF (Tipo, Ultimo_Numero) VALUES ('B04', 0);
            PRINT '✅ Tabla SECUENCIAS_NCF creada e inicializada.';
        END
        ELSE
        BEGIN
            IF NOT EXISTS (SELECT * FROM SECUENCIAS_NCF WHERE Tipo = 'B04')
            BEGIN
                INSERT INTO SECUENCIAS_NCF (Tipo, Ultimo_Numero) VALUES ('B04', 0);
                PRINT '✅ Secuencia B04 agregada.';
            END
        END
        """
        cursor.execute(sql_sequence_table)

        conn.commit()
        print("--- Configuración de Base de Datos Completada Exitosamente ---")

    except Exception as e:
        print(f"❌ Error ejecutando script SQL: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_credit_notes()
