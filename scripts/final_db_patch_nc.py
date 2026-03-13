import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

def apply_final_db_patch():
    print("--- Optimizando Procedimientos para Notas de Crédito (V9.1) ---")
    conn = db.connect()
    try:
        cursor = conn.cursor()

        # SP optimizado: Maneja nulos, espacios y errores de tipos
        sp_script = """
        CREATE OR ALTER PROCEDURE GetNotaCreditoDetalle
            @NCF_INPUT VARCHAR(50)
        AS
        BEGIN
            SET NOCOUNT ON;
            DECLARE @NCF_CLEAN VARCHAR(50) = LTRIM(RTRIM(@NCF_INPUT));
            DECLARE @ID_V INT;

            -- Buscar ID exacto o aproximado
            SELECT @ID_V = ID_VENTA FROM VENTAS WHERE NCF_GENERADO = @NCF_CLEAN;
            
            IF @ID_V IS NULL
                SELECT @ID_V = ID_VENTA FROM VENTAS WHERE NCF_GENERADO LIKE '%' + @NCF_CLEAN + '%';

            -- 1. Resultado Encabezado
            SELECT 
                ID_VENTA, 
                NCF_GENERADO, 
                TOTAL_VENTA, 
                FECHA, 
                ESTADO 
            FROM VENTAS 
            WHERE ID_VENTA = @ID_V;

            -- 2. Resultado Detalles
            SELECT 
                d.ID_PRODUCTO, 
                p.PRODUCTO, 
                d.CANTIDAD, 
                d.PRECIO_UNITARIO, 
                d.SUBTOTAL 
            FROM DETALLE_VENTAS d
            JOIN PRODUCTO p ON d.ID_PRODUCTO = p.ID_PRODUCTO
            WHERE d.ID_VENTA = @ID_V;
        END
        """
        cursor.execute(sp_script)
        conn.commit()
        print("✅ SP GetNotaCreditoDetalle actualizado y blindado.")
    except Exception as e:
        print(f"❌ Error en DB Patch: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_final_db_patch()
