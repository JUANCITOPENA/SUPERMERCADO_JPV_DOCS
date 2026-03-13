USE SUPERMERCADO_JPV_V6;
GO

-- 1. Asegurar tabla de Secuencias si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SECUENCIAS_NCF')
BEGIN
    CREATE TABLE SECUENCIAS_NCF (
        Tipo VARCHAR(10) PRIMARY KEY,
        Ultimo_Numero INT NOT NULL
    );
    INSERT INTO SECUENCIAS_NCF (Tipo, Ultimo_Numero) VALUES ('E34', 0);
END
GO

-- 2. SP para busqueda avanzada de FACTURAS para aplicarles Notas de Credito
CREATE OR ALTER PROCEDURE SP_BUSCAR_FACTURAS_PARA_NC
    @Criterio VARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP 50
        V.ID_VENTA,
        V.NCF_GENERADO,
        CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE) AS Cliente,
        V.TOTAL_VENTA,
        V.FECHA,
        V.ESTADO
    FROM VENTAS V
    INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
    WHERE (V.ESTADO = 'COMPLETADA' OR V.ESTADO = 'NC_PARCIAL')
      AND (@Criterio IS NULL OR V.NCF_GENERADO LIKE '%' + @Criterio + '%' OR C.NOMBRE_CLIENTE LIKE '%' + @Criterio + '%')
    ORDER BY V.FECHA DESC;
END
GO

-- 3. SP para crear la Nota de Credito de forma segura
CREATE OR ALTER PROCEDURE SP_CREAR_NOTA_CREDITO_PRO
    @ID_Venta INT,
    @Usuario VARCHAR(50),
    @Motivo VARCHAR(200),
    @Tipo VARCHAR(20), -- 'TOTAL' o 'PARCIAL'
    @MontoTotal DECIMAL(12,2),
    @ItbisTotal DECIMAL(12,2)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Generar NCF E34
        DECLARE @NextNum INT;
        UPDATE SECUENCIAS_NCF SET @NextNum = Ultimo_Numero = Ultimo_Numero + 1 WHERE Tipo = 'E34';
        DECLARE @NCF_NC VARCHAR(19) = 'E34' + RIGHT('0000000000' + CAST(@NextNum AS VARCHAR), 10);

        DECLARE @NCF_Orig VARCHAR(19);
        SELECT @NCF_Orig = NCF_GENERADO FROM VENTAS WHERE ID_VENTA = @ID_Venta;

        -- Insertar Cabecera
        INSERT INTO NOTA_CREDITO (ID_VENTA, NCF_NOTA_CREDITO, NCF_FACTURA_ORIGINAL, FECHA, MOTIVO, TIPO_DEVOLUCION, TOTAL_DEVUELTO, ITBIS_DEVUELTO)
        VALUES (@ID_Venta, @NCF_NC, @NCF_Orig, GETDATE(), @Motivo, @Tipo, @MontoTotal, @ItbisTotal);

        DECLARE @ID_Nota INT = SCOPE_IDENTITY();

        -- Actualizar Estado de la Venta
        DECLARE @TotalVentaOrig DECIMAL(12,2);
        SELECT @TotalVentaOrig = TOTAL_VENTA FROM VENTAS WHERE ID_VENTA = @ID_Venta;

        IF @Tipo = 'TOTAL' OR @MontoTotal >= @TotalVentaOrig
            UPDATE VENTAS SET ESTADO = 'ANULADA' WHERE ID_VENTA = @ID_Venta;
        ELSE
            UPDATE VENTAS SET ESTADO = 'NC_PARCIAL' WHERE ID_VENTA = @ID_Venta;

        COMMIT TRANSACTION;
        SELECT @ID_Nota AS ID_GENERADO, @NCF_NC AS NCF_GENERADO;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
