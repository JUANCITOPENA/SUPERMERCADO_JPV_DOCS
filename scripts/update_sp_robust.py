USE SUPERMERCADO_JPV_V6;
GO

-- Procedimiento de Busqueda Avanzada SUPER FLEXIBLE
CREATE OR ALTER PROCEDURE SP_LISTAR_NOTAS_CREDITO_AVANZADO
    @Criterio VARCHAR(100) = NULL,
    @FechaInicio DATE = NULL,
    @FechaFin DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        N.ID_NOTA,
        N.NCF_NOTA_CREDITO AS [NCF Nota],
        N.NCF_FACTURA_ORIGINAL AS [Factura Ref],
        CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE) AS Cliente,
        N.FECHA,
        N.MOTIVO,
        N.TOTAL_DEVUELTO AS Total,
        V.ID_VENTA AS [ID Venta]
    FROM NOTA_CREDITO N
    INNER JOIN VENTAS V ON N.ID_VENTA = V.ID_VENTA
    INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
    WHERE 
        (@Criterio IS NULL OR 
         N.NCF_NOTA_CREDITO LIKE '%' + @Criterio + '%' OR 
         N.NCF_FACTURA_ORIGINAL LIKE '%' + @Criterio + '%' OR
         C.NOMBRE_CLIENTE LIKE '%' + @Criterio + '%' OR
         C.RNC_CEDULA LIKE '%' + @Criterio + '%' OR
         CAST(V.ID_VENTA AS VARCHAR) = @Criterio) -- Busqueda por ID exacto
        AND (@FechaInicio IS NULL OR CAST(N.FECHA AS DATE) >= @FechaInicio)
        AND (@FechaFin IS NULL OR CAST(N.FECHA AS DATE) <= @FechaFin)
    ORDER BY N.FECHA DESC;
END
GO
