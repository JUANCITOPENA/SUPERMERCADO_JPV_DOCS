USE SUPERMERCADO_JPV_V6;
GO

CREATE OR ALTER PROCEDURE SP_POBLAR_LOGISTICA_Y_NOTAS
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Limpiar data previa de gestion para evitar duplicados
    DELETE FROM DETALLE_NOTA_CREDITO;
    DELETE FROM NOTA_CREDITO;
    DELETE FROM SEGUIMIENTO_ENTREGA;
    
    DECLARE @TotalVentas INT = (SELECT COUNT(*) FROM VENTAS);
    DECLARE @VentaID INT;
    DECLARE @FechaVenta DATETIME;
    DECLARE @NCF_Original VARCHAR(19);
    DECLARE @TotalFactura DECIMAL(12,2);
    DECLARE @ITBISFactura DECIMAL(12,2);
    DECLARE @Probabilidad FLOAT;

    -- Cursor para recorrer todas las ventas
    DECLARE cursor_ventas CURSOR FOR 
    SELECT ID_VENTA, FECHA, NCF_GENERADO, TOTAL_VENTA, TOTAL_ITBIS FROM VENTAS;

    OPEN cursor_ventas;
    FETCH NEXT FROM cursor_ventas INTO @VentaID, @FechaVenta, @NCF_Original, @TotalFactura, @ITBISFactura;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @Probabilidad = RAND();

        -- 1. LOGICA DE NOTAS DE CREDITO (5% TOTAL)
        
        -- A. CANCELACIONES (3%): Mismo dia de la venta
        IF @Probabilidad <= 0.03 
        BEGIN
            EXEC SP_GENERAR_NOTA_CREDITO @ID_Venta = @VentaID, @Motivo = 'Cancelacion por el cliente / No recibido', @EsTotal = 1;
            
            -- Registrar estatus de entrega como Cancelado
            INSERT INTO SEGUIMIENTO_ENTREGA (ID_VENTA, ID_ESTADO, COMENTARIO, UBICACION_ACTUAL, FECHA_ACTUALIZACION, ACTUALIZADO_POR)
            VALUES (@VentaID, 4, 'El cliente rechazo la mercancia al recibir', 'Punto de Entrega', @FechaVenta, 'Sistema_Auto');
        END
        
        -- B. DEVOLUCIONES (2%): 1 a 5 dias despues
        ELSE IF @Probabilidad > 0.03 AND @Probabilidad <= 0.05
        BEGIN
            DECLARE @FechaDevolucion DATETIME = DATEADD(DAY, CAST(RAND()*(5-1)+1 AS INT), @FechaVenta);
            DECLARE @NCF_Nota VARCHAR(19) = 'E34' + RIGHT('0000000000' + CAST(ABS(CHECKSUM(NEWID())) % 10000000 AS VARCHAR), 10);
            
            INSERT INTO NOTA_CREDITO (ID_VENTA, NCF_NOTA_CREDITO, NCF_FACTURA_ORIGINAL, FECHA, MOTIVO, TIPO_DEVOLUCION, TOTAL_DEVUELTO, ITBIS_DEVUELTO)
            VALUES (@VentaID, @NCF_Nota, @NCF_Original, @FechaDevolucion, 'Devolucion de mercancia por defecto', 'TOTAL', @TotalFactura, @ITBISFactura);
            
            DECLARE @ID_Nota INT = SCOPE_IDENTITY();
            INSERT INTO DETALLE_NOTA_CREDITO (ID_NOTA, ID_PRODUCTO, CANTIDAD_DEVUELTA, PRECIO_UNITARIO_REF)
            SELECT @ID_Nota, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO FROM DETALLE_VENTAS WHERE ID_VENTA = @VentaID;

            -- Actualizar estatus a Devuelto
            INSERT INTO SEGUIMIENTO_ENTREGA (ID_VENTA, ID_ESTADO, COMENTARIO, UBICACION_ACTUAL, FECHA_ACTUALIZACION, ACTUALIZADO_POR)
            VALUES (@VentaID, 3, 'Entregado inicialmente', 'Cliente', @FechaVenta, 'Sistema_Auto');
            
            INSERT INTO SEGUIMIENTO_ENTREGA (ID_VENTA, ID_ESTADO, COMENTARIO, UBICACION_ACTUAL, FECHA_ACTUALIZACION, ACTUALIZADO_POR)
            VALUES (@VentaID, 4, 'Mercancia devuelta por el cliente', 'Almacen Retorno', @FechaDevolucion, 'Sistema_Auto');
        END

        -- 2. ESTATUS PARA EL RESTO (95%)
        ELSE 
        BEGIN
            -- 90% Entregado, 10% En Ruta (Simulando pedidos recientes)
            IF RAND() > 0.1
            BEGIN
                INSERT INTO SEGUIMIENTO_ENTREGA (ID_VENTA, ID_ESTADO, COMENTARIO, UBICACION_ACTUAL, FECHA_ACTUALIZACION, ACTUALIZADO_POR)
                VALUES (@VentaID, 3, 'Entrega confirmada satisfactoriamente', 'Destino Final', DATEADD(HOUR, 2, @FechaVenta), 'Transporte_01');
            END
            ELSE
            BEGIN
                INSERT INTO SEGUIMIENTO_ENTREGA (ID_VENTA, ID_ESTADO, COMENTARIO, UBICACION_ACTUAL, FECHA_ACTUALIZACION, ACTUALIZADO_POR)
                VALUES (@VentaID, 2, 'Pedido en transito', 'Vehiculo de Reparto', @FechaVenta, 'Despacho');
            END
        END

        FETCH NEXT FROM cursor_ventas INTO @VentaID, @FechaVenta, @NCF_Original, @TotalFactura, @ITBISFactura;
    END

    CLOSE cursor_ventas;
    DEALLOCATE cursor_ventas;
END
GO

EXEC SP_POBLAR_LOGISTICA_Y_NOTAS;
GO
