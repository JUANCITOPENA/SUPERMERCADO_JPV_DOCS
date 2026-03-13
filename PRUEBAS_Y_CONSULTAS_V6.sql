USE SUPERMERCADO_JPV_V6;
GO

-- =============================================
-- 1. VALIDACION GENERAL DE VOLUMEN DE DATOS
-- =============================================
SELECT 
    (SELECT COUNT(*) FROM VENTAS) AS Total_Facturas,
    (SELECT COUNT(*) FROM NOTA_CREDITO) AS Total_Notas_Credito,
    (SELECT COUNT(*) FROM SEGUIMIENTO_ENTREGA) AS Total_Hitos_Entrega,
    FORMAT((SELECT SUM(TOTAL_VENTA) FROM VENTAS WHERE ESTADO = 'COMPLETADA'), 'N2') AS Ingresos_Brutos_Ventas,
    FORMAT((SELECT SUM(TOTAL_DEVUELTO) FROM NOTA_CREDITO), 'N2') AS Total_Descontado_Por_Devolucion;

-- =============================================
-- 2. SEGUIMIENTO DE CICLO DE VIDA (LOGISTICA)
-- =============================================
-- Ver las ultimas 20 facturas con su estado de entrega actual
SELECT TOP 20
    V.NCF_GENERADO AS Factura,
    C.NOMBRE_CLIENTE + ' ' + C.APELLIDO_CLIENTE AS Cliente,
    V.FECHA AS Fecha_Venta,
    V.ESTADO AS Estado_Factura,
    E.DESCRIPCION AS Estatus_Entrega,
    S.UBICACION_ACTUAL,
    S.COMENTARIO
FROM VENTAS V
INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
LEFT JOIN SEGUIMIENTO_ENTREGA S ON V.ID_VENTA = S.ID_VENTA
LEFT JOIN ESTADO_ENTREGA E ON S.ID_ESTADO = E.ID_ESTADO
ORDER BY V.FECHA DESC;

-- =============================================
-- 3. ANALISIS DE NOTAS DE CREDITO (NCF E34)
-- =============================================
-- Cruce entre la Nota de Credito y la Factura Original
SELECT TOP 10
    N.NCF_NOTA_CREDITO AS Nota_Credito,
    N.NCF_FACTURA_ORIGINAL AS Factura_Afectada,
    N.FECHA AS Fecha_Devolucion,
    N.MOTIVO,
    FORMAT(N.TOTAL_DEVUELTO, 'N2') AS Monto_Devuelto,
    V.FECHA AS Fecha_Original_Venta,
    DATEDIFF(DAY, V.FECHA, N.FECHA) AS Dias_Transcurridos
FROM NOTA_CREDITO N
INNER JOIN VENTAS V ON N.ID_VENTA = V.ID_VENTA
ORDER BY N.FECHA DESC;

-- =============================================
-- 4. KPI: TASA DE DEVOLUCIONES POR VENDEDOR
-- =============================================
SELECT 
    VD.VENDEDOR,
    COUNT(V.ID_VENTA) AS Total_Ventas,
    COUNT(N.ID_NOTA) AS Cantidad_Devoluciones,
    CAST(COUNT(N.ID_NOTA) * 100.0 / NULLIF(COUNT(V.ID_VENTA), 0) AS DECIMAL(5,2)) AS Tasa_Retorno_Porc
FROM VENDEDOR VD
LEFT JOIN VENTAS V ON VD.ID_VENDEDOR = V.ID_VENDEDOR
LEFT JOIN NOTA_CREDITO N ON V.ID_VENTA = N.ID_VENTA
GROUP BY VD.VENDEDOR
ORDER BY Tasa_Retorno_Porc DESC;

-- =============================================
-- 5. VALIDACION DE IMPACTO EN INVENTARIO (AUDITORIA)
-- =============================================
-- Muestra como las notas de credito afectaron el stock en tiempo real
SELECT TOP 15
    A.FECHA,
    A.ACCION,
    A.USUARIO_DB,
    A.DATOS_ANTERIORES.value('(/deleted/@PRODUCTO)[1]', 'VARCHAR(100)') AS Producto,
    A.DATOS_ANTERIORES.value('(/deleted/@STOCK)[1]', 'INT') AS Stock_Antes,
    A.DATOS_NUEVOS.value('(/inserted/@STOCK)[1]', 'INT') AS Stock_Despues,
    (A.DATOS_NUEVOS.value('(/inserted/@STOCK)[1]', 'INT') - A.DATOS_ANTERIORES.value('(/deleted/@STOCK)[1]', 'INT')) AS Variacion
FROM TABLA_AUDITORIA A
WHERE TABLA_AFECTADA = 'PRODUCTO'
ORDER BY A.FECHA DESC;
