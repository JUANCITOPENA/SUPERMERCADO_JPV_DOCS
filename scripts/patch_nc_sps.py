import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db

def apply_sp_patch():
    print("--- Creando Procedimientos Almacenados para Notas de Crédito ---")
    
    conn = db.connect()
    try:
        cursor = conn.cursor()

        # 1. SP para obtener detalle de factura para NC
        sp_get_invoice = """
        CREATE OR ALTER PROCEDURE GetNotaCreditoDetalle
            @NCF VARCHAR(20)
        AS
        BEGIN
            -- Encabezado
            SELECT ID_VENTA, NCF_GENERADO, TOTAL_VENTA, FECHA, ESTADO 
            FROM VENTAS 
            WHERE NCF_GENERADO = @NCF;

            -- Detalles
            SELECT d.ID_PRODUCTO, p.PRODUCTO, d.CANTIDAD, d.PRECIO_UNITARIO, d.SUBTOTAL 
            FROM DETALLE_VENTAS d
            JOIN PRODUCTO p ON d.ID_PRODUCTO = p.ID_PRODUCTO
            WHERE d.ID_VENTA = (SELECT ID_VENTA FROM VENTAS WHERE NCF_GENERADO = @NCF);
        END
        """
        cursor.execute(sp_get_invoice)
        print("✅ SP GetNotaCreditoDetalle creado/actualizado.")

        # 2. SP para crear la Nota de Crédito (Lógica Transaccional)
        # Nota: Usaremos lógica en el controlador para mayor flexibilidad con los items, 
        # pero el SP GetNotaCreditoDetalle ya resuelve la búsqueda fallida.
        
        conn.commit()
        print("--- Parche de Base de Datos Aplicado ---")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    apply_sp_patch()
