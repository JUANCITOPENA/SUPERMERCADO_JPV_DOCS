import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

def update_sp_robust():
    print("--- Optimizando Procedimiento Almacenado GetNotaCreditoDetalle ---")
    
    conn = db.connect()
    try:
        cursor = conn.cursor()

        # SP Robusto con SET NOCOUNT ON y manejo de espacios
        sp_get_invoice = """
        CREATE OR ALTER PROCEDURE GetNotaCreditoDetalle
            @NCF VARCHAR(50)
        AS
        BEGIN
            SET NOCOUNT ON;
            DECLARE @ID_V INT;
            
            -- Limpiar entrada
            SET @NCF = LTRIM(RTRIM(@NCF));

            -- Buscar ID Venta primero
            SELECT @ID_V = ID_VENTA FROM VENTAS WHERE NCF_GENERADO = @NCF;

            -- 1. Encabezado
            SELECT ID_VENTA, NCF_GENERADO, TOTAL_VENTA, FECHA, ESTADO 
            FROM VENTAS 
            WHERE ID_VENTA = @ID_V;

            -- 2. Detalles
            SELECT d.ID_PRODUCTO, p.PRODUCTO, d.CANTIDAD, d.PRECIO_UNITARIO, d.SUBTOTAL 
            FROM DETALLE_VENTAS d
            JOIN PRODUCTO p ON d.ID_PRODUCTO = p.ID_PRODUCTO
            WHERE d.ID_VENTA = @ID_V;
        END
        """
        cursor.execute(sp_get_invoice)
        conn.commit()
        print("✅ SP GetNotaCreditoDetalle actualizado con éxito.")

    except Exception as e:
        print(f"❌ Error actualizando SP: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_sp_robust()
