# 🛒 SUPERMERCADO_JPV_V6 - Sistema de Gestion Integral

![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)
![Database](https://img.shields.io/badge/database-SQL_Server-red.svg)
![Status](https://img.shields.io/badge/status-Production-green.svg)

---

## 1. 🚩 Planteamiento del Problema
La gestion manual o fragmentada de un supermercado conlleva errores en inventarios, lentitud en la facturacion y falta de visibilidad en las finanzas. **SUPERMERCADO_JPV_V6** nace de la necesidad de unificar todos los procesos de negocio (Ventas, Compras, Inventario, RRHH) en una unica fuente de verdad transaccional, robusta y escalable.

---

## 2. 📖 Introduccion
Este proyecto constituye el **nucleo de datos** para el ERP del supermercado. Disenado bajo estandares de normalizacion (3NF), soporta operaciones concurrentes de multiples cajas y puntos de administracion. La arquitectura esta orientada a mantener la integridad referencial estricta y proporcionar datos analiticos en tiempo real.

---

## 3. 🎯 Objetivos (SMART)
*   **S**pecific: Centralizar la data de ventas, stock y clientes.
*   **M**easurable: Reducir el tiempo de cuadre de caja en un 90%.
*   **A**ttainable: Utilizando SQL Server Enterprise/Developer edition.
*   **R**elevant: Critico para la toma de decisiones gerenciales.
*   **T**ime-bound: Operativo 24/7 con backups automatizados.

---

## 4. 🔭 Alcance
El sistema abarca los siguientes modulos de datos:
*   ✅ **Inventario:** Productos, Categorias, Unidades, Movimientos.
*   ✅ **Ventas:** Facturacion, Detalle, Cajas, Turnos.
*   ✅ **Compras:** Suplidores, Ordenes de Compra, Cuentas por Pagar.
*   ✅ **Seguridad:** Usuarios, Roles, Auditoria.
*   ✅ **Entidades:** Clientes, Empleados.

---

## 5. 🛠 Tecnologias y Stack
| Componente | Tecnologia | Descripcion |
| :--- | :--- | :--- |
| **Motor DB** | Microsoft SQL Server | Version 2019 o superior. |
| **Lenguaje** | T-SQL | Transact-SQL para logica de negocio. |
| **Integracion** | .NET / C# | Compatible con Entity Framework / Dapper. |
| **Reportes** | SSRS / PowerBI | Estructura optimizada para BI. |

---

## 6. ⚙ Instalacion y Despliegue

### Requisitos Previos
*   Instancia de SQL Server activa.
*   Acceso con privilegios `db_owner` o `sysadmin`.

### Paso a Paso
1.  **Clonar Repositorio:** Descargue los scripts DDL.
2.  **Crear Base de Datos:**
    ```sql
    CREATE DATABASE SUPERMERCADO_JPV_V6;
    ```
3.  **Ejecutar Scripts:** Corra el script `schema.sql` seguido de `seed_data.sql`.
4.  **Configurar Cadena de Conexion:**
    `Server=10.0.0.15;Database=SUPERMERCADO_JPV_V6;User Id=JUANCITO;Password=123456;`

---

## 7. 🚀 Uso y Operacion
El sistema esta disenado para ser consumido por una API o Aplicacion de Escritorio.
*   **Transacciones:** Utilizar los Stored Procedures `sp_RegistrarVenta`, `sp_ActualizarStock`.
*   **Consultas:** Usar las Vistas `vw_ReporteVentas`, `vw_StockBajo` para lectura.
*   **Mantenimiento:** Reconstruccion de indices semanal (domingos 3 AM).

---

## 8. 💡 Ejemplos de Consultas

**Obtener Top 5 Productos mas vendidos:**
```sql
SELECT TOP 5 p.Nombre, SUM(dv.Cantidad) as TotalVendido
FROM DETALLE_VENTA dv
JOIN PRODUCTO p ON dv.IdProducto = p.Id
GROUP BY p.Nombre
ORDER BY TotalVendido DESC;
```

---

## 9. 🧠 Modelo de Datos Tecnico (Detallado)


```sql
/*
   =============================================================================
   SCRIPT BASE DE DATOS: SUPERMERCADO_JPV_V6 (EDICION DOMINICANA / DGII)
   FECHA: 15 DE ENERO, 2026
   AUTOR: ASISTENTE IA
   DESCRIPCIÓN: 
     - INCLUYE CONTROL DE NCF (FISCAL B01 / CONSUMIDOR B02)
     - MANEJO DE RNC / CÉDULA
     - CONDICIONES DE PAGO (CONTADO, CRÉDITO, TRANSFERENCIA)
     - TIPOS DE ENTREGA (ONLINE/DELIVERY vs TIENDA)
     - MANTIENE TODA LA DATA HISTÓRICA E IMÁGENES PREVIAS
   =============================================================================
*/

USE master;
GO

IF EXISTS(SELECT * FROM sys.databases WHERE name = 'SUPERMERCADO_JPV_V6')
BEGIN
    ALTER DATABASE SUPERMERCADO_JPV_V6 SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE SUPERMERCADO_JPV_V6;
END
GO

CREATE DATABASE SUPERMERCADO_JPV_V6;
GO
USE SUPERMERCADO_JPV_V6;
GO

-- 1. TABLAS CATÁLOGOS Y MAESTRAS (MEJORADAS)
```
### 📁 1.1 Regiones y Provincias (Geografía)

```sql
CREATE TABLE REGION (
    ID_REGION INT PRIMARY KEY,
    REGION VARCHAR(50) NOT NULL,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE PROVINCIAS (
    id_provincia INT PRIMARY KEY,
    nombreProvincia VARCHAR(100) NOT NULL,
    id_region INT NOT NULL FOREIGN KEY REFERENCES REGION(ID_REGION),
    latitud DECIMAL(9,6) NULL,
    longitud DECIMAL(9,6) NULL
);
```
### 📁 1.2 Género

```sql
CREATE TABLE Genero (
    ID_Genero INT PRIMARY KEY,
    Genero VARCHAR(50) NOT NULL
);
```
### 📁 1.3 NUEVO: Tipos de NCF (Comprobantes Fiscales DGII)

```sql
-- Se mapea lo que pediste: "31" para Crédito Fiscal (B01) y "32" para Consumidor Final (B02)
CREATE TABLE TIPO_NCF (
    ID_TIPO_NCF INT PRIMARY KEY,
    CODIGO_INTERNO VARCHAR(10) NOT NULL, -- Ej: '31', '32'
    DESCRIPCION VARCHAR(100) NOT NULL,   -- Ej: 'Factura de Crédito Fiscal'
    SERIE_NCF VARCHAR(3) NOT NULL,       -- Ej: 'B01', 'B02'
    REQUIERE_RNC BIT DEFAULT 0           -- 1 = Si, 0 = No
);
```
### 📁 1.4 NUEVO: Condiciones de Pago

```sql
CREATE TABLE CONDICION_PAGO (
    ID_CONDICION INT PRIMARY KEY,
    NOMBRE_CONDICION VARCHAR(50) NOT NULL, -- Contado, Crédito 30 días, etc.
    ES_CREDITO BIT DEFAULT 0               -- Define si genera deuda
);
```
### 📁 1.5 NUEVO: Método de Pago (El instrumento financiero)

```sql
CREATE TABLE METODO_PAGO (
    ID_METODO INT PRIMARY KEY,
    METODO VARCHAR(50) NOT NULL -- Efectivo, Tarjeta, Cheque, Transferencia
);
```
### 📁 1.6 NUEVO: Método de Entrega (Logística)

```sql
CREATE TABLE METODO_ENTREGA (
    ID_ENTREGA INT PRIMARY KEY,
    TIPO_ENTREGA VARCHAR(50) NOT NULL, -- Pickup (Tienda), Delivery Local, Envíos Nacionales
    ES_ONLINE BIT DEFAULT 0
);
```
### 📁 1.7 CLIENTE (MEJORADO CON RNC Y CRÉDITO)

```sql
CREATE TABLE CLIENTE (
    ID_CLIENTE INT PRIMARY KEY,
    NOMBRE_CLIENTE VARCHAR(100) NOT NULL,
    APELLIDO_CLIENTE VARCHAR(100) NOT NULL,
    
    -- Datos Fiscales Rep. Dom.
    RNC_CEDULA VARCHAR(20) NOT NULL, -- Puede ser Cédula (11) o RNC (9)
    TIPO_PERSONA VARCHAR(20) NOT NULL, -- 'FISICA' o 'JURIDICA'
    
    -- Datos de Crédito
    TIENE_CREDITO_APROBADO BIT DEFAULT 0,
    LIMITE_CREDITO DECIMAL(12,2) DEFAULT 0,
    
    -- Ubicación
    DIRECCION VARCHAR(200) NULL,
    id_region INT NOT NULL FOREIGN KEY REFERENCES REGION(ID_REGION),
    id_provincia INT NULL FOREIGN KEY REFERENCES PROVINCIAS(id_provincia),
    
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE()
);
```
### 📁 1.8 VENDEDOR (Mantenemos estructura)

```sql
CREATE TABLE VENDEDOR (
    ID_VENDEDOR INT PRIMARY KEY,
    VENDEDOR VARCHAR(100) NOT NULL,
    id_genero INT NULL FOREIGN KEY REFERENCES Genero(ID_Genero),
    SUCURSAL VARCHAR(100) NULL,
    PROVINCIA INT NOT NULL FOREIGN KEY REFERENCES PROVINCIAS(id_provincia),
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE FOTOS_VENDEDOR (
    ID_Foto INT PRIMARY KEY,
    foto_Vendedor_url VARCHAR(255) NOT NULL,
    ID_vendedor INT NOT NULL FOREIGN KEY REFERENCES VENDEDOR(ID_VENDEDOR)
);
```
### 📁 1.9 PRODUCTOS

```sql
CREATE TABLE PRODUCTO (
    ID_PRODUCTO INT PRIMARY KEY,
    PRODUCTO VARCHAR(100) NOT NULL,
    STOCK INT NOT NULL,
    PRECIO_COMPRA DECIMAL(9,2) NOT NULL,
    PRECIO_VENTA DECIMAL(9,2) NOT NULL,
    GRAVADO_ITBIS BIT DEFAULT 1, -- Indica si paga impuesto
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE FOTO_PRODUCTOS (
    ID_Foto INT PRIMARY KEY,
    foto_Productos_url VARCHAR(255) NOT NULL,
    ID_PRODUCTO INT NOT NULL FOREIGN KEY REFERENCES PRODUCTO(ID_PRODUCTO)
);
```
### 📁 1.10 USUARIOS (Seguridad)

```sql
-- ESTRUCTURA TABLA USUARIOS (CON ENCRIPTACIÓN)

IF OBJECT_ID('USUARIOS', 'U') IS NOT NULL
BEGIN
    DROP TABLE USUARIOS;
END
GO

CREATE TABLE USUARIOS (
    ID_USUARIO INT PRIMARY KEY,
    NOMBRE_USUARIO VARCHAR(50) UNIQUE NOT NULL,
    -- Cambio: VARBINARY para almacenar el Hash en lugar de texto plano
    PASSWORD VARBINARY(64) NOT NULL, 
    ROL VARCHAR(20) NOT NULL, 
    ID_REGION INT NULL FOREIGN KEY REFERENCES REGION(ID_REGION),
    fecha_creacion DATETIME DEFAULT GETDATE()
);
GO



-- 2. ESTRUCTURA TRANSACCIONAL (VENTAS CON DGII)
```
### 📁 2.1 Tabla Cabecera (La Factura)

```sql
CREATE TABLE VENTAS (
    ID_VENTA INT PRIMARY KEY IDENTITY(1,1),
    FECHA DATETIME NOT NULL,
    
    -- Relaciones
    ID_CLIENTE INT NOT NULL FOREIGN KEY REFERENCES CLIENTE(ID_CLIENTE),
    ID_VENDEDOR INT NOT NULL FOREIGN KEY REFERENCES VENDEDOR(ID_VENDEDOR),
    ID_REGION INT NOT NULL FOREIGN KEY REFERENCES REGION(ID_REGION),
    
    -- Condiciones Comerciales
    ID_CONDICION INT NOT NULL FOREIGN KEY REFERENCES CONDICION_PAGO(ID_CONDICION),
    ID_METODO_PAGO INT NOT NULL FOREIGN KEY REFERENCES METODO_PAGO(ID_METODO),
    ID_ENTREGA INT NOT NULL FOREIGN KEY REFERENCES METODO_ENTREGA(ID_ENTREGA),
    
    -- Datos Fiscales (DGII)
    ID_TIPO_NCF INT NOT NULL FOREIGN KEY REFERENCES TIPO_NCF(ID_TIPO_NCF),
    NCF_GENERADO VARCHAR(19) NOT NULL, -- Ej: B0100000001
    
    -- Totales
    SUBTOTAL_VENTA DECIMAL(12,2) DEFAULT 0,
    TOTAL_ITBIS DECIMAL(12,2) DEFAULT 0,
    TOTAL_VENTA DECIMAL(12,2) DEFAULT 0,
    
    ESTADO VARCHAR(20) DEFAULT 'COMPLETADA', -- PENDIENTE, PAGADA, CANCELADA
    
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```
### 📁 2.2 Tabla Detalle
```sql
CREATE TABLE DETALLE_VENTAS (
    ID_DETALLE INT PRIMARY KEY IDENTITY(1,1),
    ID_VENTA INT NOT NULL FOREIGN KEY REFERENCES VENTAS(ID_VENTA),
    ID_PRODUCTO INT NOT NULL FOREIGN KEY REFERENCES PRODUCTO(ID_PRODUCTO),
    
    CANTIDAD INT NOT NULL,
    PRECIO_UNITARIO DECIMAL(9,2) NOT NULL, 
    ITBIS_UNITARIO DECIMAL(9,2) DEFAULT 0,
    SUBTOTAL DECIMAL(12,2) NOT NULL,       
    
    fecha_creacion DATETIME DEFAULT GETDATE()
);
GO

-- 3. INSERCIÓN DE DATOS MAESTROS

-- Geografía
INSERT INTO REGION (ID_REGION, REGION) VALUES (1, 'NORTE'), (2, 'SUR'), (3, 'ESTE'), (4, 'OESTE');

INSERT INTO PROVINCIAS (id_provincia, nombreProvincia, id_region, latitud, longitud) VALUES
(1, 'La Altagracia', 1, 18.616667, -68.633333),
(2, 'El Seibo', 1, 18.766667, -69.033333),
(3, 'Hato Mayor', 1, 18.750000, -69.250000),
(4, 'La Romana', 1, 18.433333, -68.966667),
(5, 'San Pedro de Macorís', 1, 18.450000, -69.300000),
(6, 'Santiago', 2, 19.450000, -70.700000),
(7, 'Puerto Plata', 2, 19.800000, -70.700000),
(8, 'Duarte', 2, 19.300000, -70.100000),
(9, 'Espaillat', 2, 19.600000, -70.350000),
(10, 'La Vega', 2, 19.216667, -70.516667),
(11, 'Azua', 3, 18.450000, -70.733333),
(12, 'Barahona', 3, 18.200000, -71.100000),
(13, 'San Juan', 3, 18.800000, -71.200000),
(14, 'San Cristóbal', 3, 18.416667, -70.100000),
(15, 'Peravia', 3, 18.283333, -70.350000);

-- Género
INSERT INTO Genero (ID_Genero, Genero) VALUES (1, 'Masculino'), (2, 'Femenino');

-- NUEVO: Tipos de NCF
INSERT INTO TIPO_NCF (ID_TIPO_NCF, CODIGO_INTERNO, SERIE_NCF, DESCRIPCION, REQUIERE_RNC) VALUES
(1, '31', 'B01', 'VALOR FISCAL (Crédito Fiscal)', 1),
(2, '32', 'B02', 'CONSUMIDOR FINAL', 0),
(3, '34', 'B04', 'NOTA DE CRÉDITO', 0),
(4, '44', 'B14', 'RÉGIMEN ESPECIAL', 1);

-- NUEVO: Condiciones de Pago
INSERT INTO CONDICION_PAGO (ID_CONDICION, NOMBRE_CONDICION, ES_CREDITO) VALUES
(1, 'Contado', 0),
(2, 'Crédito 15 Días', 1),
(3, 'Crédito 30 Días', 1);

-- NUEVO: Métodos de Pago
INSERT INTO METODO_PAGO (ID_METODO, METODO) VALUES
(1, 'Efectivo'),
(2, 'Tarjeta de Crédito/Débito'),
(3, 'Transferencia Bancaria'),
(4, 'Cheque');

-- NUEVO: Métodos de Entrega
INSERT INTO METODO_ENTREGA (ID_ENTREGA, TIPO_ENTREGA, ES_ONLINE) VALUES
(1, 'Retiro en Tienda (Offline)', 0),
(2, 'Delivery Local', 1),
(3, 'Envío Nacional (MetroPac/Caribe Tours)', 1);

-- CLIENTES (Actualizado con RNC y Lógica de Negocio)
-- Asignamos RNCs ficticios y Límites de crédito a algunos
INSERT INTO CLIENTE (ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, id_region, id_provincia, RNC_CEDULA, TIPO_PERSONA, TIENE_CREDITO_APROBADO, LIMITE_CREDITO, DIRECCION) VALUES 
(1, 'Alejandro', 'Perez', 1, 1, '001-0012345-1', 'FISICA', 0, 0, 'Av. Libertad #23'), 
(2, 'María', 'Vizcaino', 2, 6, '131-2345678-2', 'JURIDICA', 1, 50000, 'Calle El Sol #4, Zona Monumental'), 
(3, 'José', 'Santana', 1, 2, '001-9988776-3', 'FISICA', 0, 0, 'Calle Duarte #10'),
(4, 'Laura', 'Diaz', 2, 7, '402-1122334-4', 'JURIDICA', 1, 100000, 'Malecon #55'), 
(5, 'Carlos', 'Bergara', 1, 3, '001-5544332-5', 'FISICA', 0, 0, 'Sector Los Cajuiles'), 
(6, 'Lucía', 'Ramos', 2, 8, '056-0000123-1', 'FISICA', 0, 0, 'Av. 27 de Febrero'),
(7, 'Juan', 'Comila', 1, 4, '101-5555555-5', 'JURIDICA', 1, 75000, 'Zona Franca La Romana'), 
(8, 'Ana', 'Gabriel', 2, 9, '001-0000001-1', 'FISICA', 0, 0, 'Calle Mella'), 
(9, 'Luis', 'Diaz', 1, 5, '402-9999999-9', 'FISICA', 1, 5000, 'Barrio Restauracion'),
(10, 'Carmen', 'Santana', 2, 10, '130-1212121-2', 'JURIDICA', 1, 200000, 'Av. Rivas'), 
(11, 'Miguel', 'Ramos', 1, 1, '223-3344556-6', 'FISICA', 0, 0, 'Higüey Centro'), 
(12, 'Sofía', 'Comila', 2, 6, '031-1111222-2', 'FISICA', 0, 0, 'Los Jardines'),
(13, 'Pablo', 'Perez', 1, 2, '001-1234567-8', 'FISICA', 0, 0, 'El Seibo'), 
(14, 'Isabel', 'Vizcaino', 2, 7, '102-3333333-3', 'JURIDICA', 1, 60000, 'Plaza Turistica'), 
(15, 'Diego', 'Santana', 1, 3, '402-8888888-8', 'FISICA', 0, 0, 'Hato Mayor'),
(16, 'Paula', 'Diaz', 2, 8, '001-7777777-7', 'FISICA', 0, 0, 'San Francisco'), 
(17, 'Francisco', 'Bergara', 1, 4, '131-5556667-7', 'JURIDICA', 1, 150000, 'Casa de Campo'), 
(18, 'Marta', 'Ramos', 2, 9, '054-2222222-2', 'FISICA', 0, 0, 'Moca Centro'),
(19, 'Antonio', 'Comila', 1, 5, '001-4444444-4', 'FISICA', 0, 0, 'SPM Malecón'), 
(20, 'Elena', 'Gabrie', 2, 10, '402-3332221-1', 'FISICA', 1, 10000, 'La Vega'), 
(21, 'Javier', 'Diaz', 1, 1, '001-1111111-1', 'FISICA', 0, 0, 'Bavaro'),
(22, 'Sara', 'Santana', 2, 6, '031-9999999-9', 'JURIDICA', 1, 80000, 'Gurabo'), 
(23, 'Andrés', 'Ramos', 1, 2, '001-6666666-6', 'FISICA', 0, 0, 'Miches'), 
(24, 'Claudia', 'Comila', 2, 7, '402-5555555-5', 'FISICA', 0, 0, 'Sosua'),
(25, 'Manuel', 'Perez', 1, 3, '101-2222222-2', 'JURIDICA', 1, 300000, 'Sabana de la Mar'), 
(26, 'Patricia', 'Vizcaino', 2, 8, '001-8888888-8', 'FISICA', 0, 0, 'Tenares'), 
(27, 'David', 'Santana', 1, 4, '023-1111111-1', 'FISICA', 0, 0, 'Villa Hermosa'),
(28, 'Teresa', 'Lopez', 2, 9, '402-0000000-0', 'FISICA', 0, 0, 'Gaspar Hernandez'), 
(29, 'Sergio', 'Bergara', 1, 5, '001-2323232-3', 'FISICA', 0, 0, 'Consuelo'), 
(30, 'Julia', 'Ramos', 2, 10, '131-9876543-2', 'JURIDICA', 1, 40000, 'Constanza');

SELECT * FROM CLIENTE


USE SUPERMERCADO_JPV_V6;
GO

-- 1. LIMPIEZA DE OBSTÁCULOS (Desconectar referencias)

-- Primero, buscamos si existe la restricción en VENTAS que apunta a VENDEDOR y la borramos
DECLARE @ConstraintName NVARCHAR(200);
SELECT @ConstraintName = name 
FROM sys.foreign_keys 
WHERE parent_object_id = OBJECT_ID('VENTAS') AND referenced_object_id = OBJECT_ID('VENDEDOR');

IF @ConstraintName IS NOT NULL
BEGIN
    DECLARE @SQL NVARCHAR(MAX) = 'ALTER TABLE VENTAS DROP CONSTRAINT ' + @ConstraintName;
    EXEC(@SQL);
    PRINT 'Restricción en VENTAS eliminada temporalmente.';
END

-- Borramos la tabla de fotos (hija directa)
IF OBJECT_ID('FOTOS_VENDEDOR', 'U') IS NOT NULL 
    DROP TABLE FOTOS_VENDEDOR;

-- Ahora sí podemos borrar VENDEDOR
IF OBJECT_ID('VENDEDOR', 'U') IS NOT NULL 
    DROP TABLE VENDEDOR;
GO

-- 2. ASEGURAR DATOS PREVIOS (Evita el Error 547)
-- Si Genero o Provincias no existen, los inserts fallarán. Esto lo asegura:

IF NOT EXISTS (SELECT * FROM Genero WHERE ID_Genero = 1)
    INSERT INTO Genero (ID_Genero, Genero) VALUES (1, 'Masculino');

IF NOT EXISTS (SELECT * FROM Genero WHERE ID_Genero = 2)
    INSERT INTO Genero (ID_Genero, Genero) VALUES (2, 'Femenino');

-- (Nota: Asumimos que PROVINCIAS ya tiene datos del script anterior. 
-- Si PROVINCIAS está vacía, necesitarás correr los inserts de provincias de nuevo).

-- 3. CREACIÓN DE TABLAS CORREGIDAS

CREATE TABLE VENDEDOR (
    ID_VENDEDOR INT PRIMARY KEY,
    VENDEDOR VARCHAR(100) NOT NULL,
    id_genero INT NULL FOREIGN KEY REFERENCES Genero(ID_Genero),
    SUCURSAL VARCHAR(100) NULL,
    PROVINCIA INT NOT NULL FOREIGN KEY REFERENCES PROVINCIAS(id_provincia),
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE FOTOS_VENDEDOR (
    ID_Foto INT PRIMARY KEY,
    foto_Vendedor_url VARCHAR(500) NOT NULL, -- Aumentado a 500 por seguridad
    ID_vendedor INT NOT NULL FOREIGN KEY REFERENCES VENDEDOR(ID_VENDEDOR)
);
GO

-- 4. INSERTAR DATOS (Orden Explícito para evitar errores)

-- IMPORTANTE: El orden aquí es (ID, NOMBRE, GENERO, PROVINCIA, SUCURSAL)
INSERT INTO VENDEDOR (ID_VENDEDOR, VENDEDOR, id_genero, PROVINCIA, SUCURSAL) VALUES 
(1, 'Juan Perez', 1, 1, 'Sucursal 1'),
(2, 'Maria Vizcaino', 2, 6, 'Sucursal 2'), -- Corregido prov 6 (Stgo) para coincidir con tu data original
(3, 'Ana Santana', 2, 2, 'Sucursal 1'),
(4, 'Luis Diaz', 1, 7, 'Sucursal 1'),
(5, 'Sofia Bergara', 2, 3, 'Sucursal 1'), 
(6, 'Jorge Ramos', 1, 8, 'Sucursal 2'), 
(7, 'Juan Comila', 1, 4, 'Sucursal 2'), 
(8, 'Juan Gabriel', 1, 9, 'Sucursal 2'), 
(9, 'Carlos Santos', 1, 5, 'Sucursal 2'), 
(10, 'Julio Linarez', 1, 10, 'Sucursal 2'), 
(11, 'Pedro Gómez', 1, 11, 'Sucursal 3'), 
(12, 'María Rodríguez', 2, 12, 'Sucursal 3'),
(13, 'Alejandro Peña', 1, 13, 'Sucursal 3'), 
(14, 'Lucía Ramirez', 2, 14, 'Sucursal 3'), 
(15, 'Laura de la Rosa', 2, 15, 'Sucursal 3');

-- Insertar Fotos
INSERT INTO FOTOS_VENDEDOR (ID_FOTO, ID_VENDEDOR, FOTO_VENDEDOR_URL) VALUES
(1, 1, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_1.png'),
(2, 2, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_2.png'),
(3, 3, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_3.png'),
(4, 4, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_4.png'),
(5, 5, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_5.png'),
(6, 6, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_6.png'),
(7, 7, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_7.png'),
(8, 8, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_8.png'),
(9, 9, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_9.png'),
(10, 10, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_10.png'),
(11, 11, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_11.png'),
(12, 12, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_12.png'),
(13, 13, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_13.png'),
(14, 14, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_14.png'),
(15, 15, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PERSONAS/persona_15.png');
GO

-- 5. RECONEXIÓN (Restaurar integridad con Ventas)
-- Volvemos a agregar la llave foránea a VENTAS para proteger los datos futuros
ALTER TABLE VENTAS 
ADD CONSTRAINT FK_VENTAS_VENDEDOR FOREIGN KEY (ID_VENDEDOR) REFERENCES VENDEDOR(ID_VENDEDOR);
GO

-- Verificación final
SELECT TOP 5 * FROM VENDEDOR;
SELECT TOP 5 * FROM FOTOS_VENDEDOR;





-- PRODUCTOS
INSERT INTO dbo.PRODUCTO (ID_PRODUCTO, PRODUCTO, STOCK, PRECIO_COMPRA, PRECIO_VENTA) VALUES
(1, 'Leche', 200, 50, 70), (2, 'Legumbres', 200, 30, 50), (3, 'Frutas frescas', 200, 20, 40),
(4, 'Pan integral', 200, 40, 60), (5, 'Aceite', 200, 45, 65), (6, 'Arroz', 200, 25, 45),
(7, 'Huevos', 200, 35, 55), (8, 'Yogur', 200, 30, 50), (9, 'Aceite de oliva', -203, 60, 80),
(10, 'Agua potable', 200, 10, 30), (11, 'Verduras frescas', 200, 15, 35), (12, 'Carne de pollo', -204, 55, 75),
(13, 'Pescado', 200, 50, 70), (14, 'Queso', 196, 65, 85), (15, 'Miel', 160, 75, 95),
(16, 'Mermelada de Manzanas', 200, 76, 112), (17, 'Jabon Limpiol', 60, 85, 110), (18, 'Crema dental Colgate', 0, 112, 175),
(19, 'Cebolla Criolla', 200, 65, 100), (20, 'Gustocita', 140, 6, 10), (21, 'Cubito Maggi', 160, 5.5, 10),
(22, 'Mantequilla Rica', 180, 120, 175), (23, 'Avena Quaker', 200, 75, 110);

INSERT INTO FOTO_PRODUCTOS (ID_Foto, ID_PRODUCTO, foto_Productos_url) VALUES 
(1, 1, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_1.png'),
(2, 2, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_2.png'),
(3, 3, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_3.png'),
(4, 4, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_4.png'),
(5, 5, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_5.png'),
(6, 6, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_6.png'),
(7, 7, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_7.png'),
(8, 8, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_8.png'),
(9, 9, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_9.png'),
(10, 10, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_10.png'),
(11, 11, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_11.png'),
(12, 12, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_12.png'),
(13, 13, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_13.png'),
(14, 14, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_14.png'),
(15, 15, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_15.png'),
(16, 16, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_16.png'),
(17, 17, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_17.png'),
(18, 18, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_18.png'),
(19, 19, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_19.png'),
(20, 20, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_20.png'),
(21, 21, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_21.png'),
(22, 22, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_22.png'),
(23, 23, 'https://raw.githubusercontent.com/JUANCITOPENA/GENERADOR_IMAGENES_PERSONAS/refs/heads/main/FOTOS_PRODUCTOS/producto_23.png');

-- USUARIOS
-- INSERTAR REGISTROS (ENCRIPTANDO '123456')
-- Nota: HASHBYTES('SHA2_256', 'TuPassword') convierte el texto en un código binario seguro.

INSERT INTO USUARIOS (ID_USUARIO, NOMBRE_USUARIO, PASSWORD, ROL, ID_REGION) VALUES 
(1, 'Juancito', HASHBYTES('SHA2_256', '123456'), 'admin', NULL),
(2, 'Dariel', HASHBYTES('SHA2_256', '123456'), 'supervisor', NULL),
(3, 'Juan.Perez', HASHBYTES('SHA2_256', '123456'), 'vendedor', 1),
(4, 'Maria.Vizcaino', HASHBYTES('SHA2_256', '123456'), 'vendedor', 1),
(5, 'Ana.Santana', HASHBYTES('SHA2_256', '123456'), 'vendedor', 1),
(6, 'Luis.Diaz', HASHBYTES('SHA2_256', '123456'), 'vendedor', 1),
(7, 'Jorge.Ramos', HASHBYTES('SHA2_256', '123456'), 'vendedor', 2),
(8, 'Juan.Comila', HASHBYTES('SHA2_256', '123456'), 'vendedor', 2),
(9, 'Pedro.Gómez', HASHBYTES('SHA2_256', '123456'), 'vendedor', 3),
(10, 'María.Rodríguez', HASHBYTES('SHA2_256', '123456'), 'vendedor', 3);
GO

-- EJEMPLO DE CÓMO VALIDAR EL LOGIN (PRUEBA)
/*
   Para verificar si una contraseña es correcta en tu sistema (Login),
   comparas el Hash de lo que escribe el usuario con el Hash guardado en la BD.
*/

-- Ejemplo: Validando el usuario 'Juancito' con clave '123456'
SELECT ID_USUARIO, NOMBRE_USUARIO, ROL 
FROM USUARIOS 
WHERE NOMBRE_USUARIO = 'Juancito' 
AND PASSWORD = HASHBYTES('SHA2_256', '123456');


SELECT * FROM USUARIOS




-- 4. GENERACIÓN INTELIGENTE DE DATOS (SIMULACIÓN DE NEGOCIO REAL)
USE SUPERMERCADO_JPV_V6;
GO

-- 1. ACTUALIZAR CATÁLOGO DE NCF (SEGÚN TU IMAGEN - e-CF)
-- Borramos los viejos tipos B01, B02...
DELETE FROM TIPO_NCF;

-- Insertamos los nuevos tipos de Facturación Electrónica (Serie E)
INSERT INTO TIPO_NCF (ID_TIPO_NCF, CODIGO_INTERNO, SERIE_NCF, DESCRIPCION, REQUIERE_RNC) VALUES
(1, '31', 'E31', 'Factura de Crédito Fiscal Electrónica', 1),
(2, '32', 'E32', 'Factura de Consumo Electrónica', 0),
(3, '44', 'E44', 'Comprobante para Regímenes Especiales', 1),
(4, '45', 'E45', 'Comprobante Gubernamental', 1);
GO

-- 2. LIMPIEZA DE DATOS (Para regenerar con formato E)
DELETE FROM DETALLE_VENTAS;
DELETE FROM VENTAS;
DBCC CHECKIDENT ('DETALLE_VENTAS', RESEED, 0);
DBCC CHECKIDENT ('VENTAS', RESEED, 0);
GO

-- 3. GENERADOR DE VENTAS (CORREGIDO: FECHAS + SERIE E)
SET NOCOUNT ON;

DECLARE @FechaInicio DATE = '2023-01-01';
DECLARE @FechaFin DATE = '2025-12-31';
DECLARE @CantidadVentas INT = 2000; 

-- Variables de control
DECLARE @i INT = 0;
DECLARE @NuevaVentaID INT;
DECLARE @FechaVenta DATETIME; 
DECLARE @BaseFecha DATE;
DECLARE @ID_CLIENTE INT;
DECLARE @ID_VENDEDOR INT;
DECLARE @ID_REGION INT;

-- Variables de Negocio (DGII)
DECLARE @TipoCliente VARCHAR(20);
DECLARE @ID_TIPO_NCF INT;
DECLARE @SerieNCF VARCHAR(3);
DECLARE @SecuenciaNCF BIGINT; -- Usamos BIGINT por si el secuencial es muy grande
DECLARE @NCF_Full VARCHAR(19);

-- Variables Pago y Entrega
DECLARE @TieneCredito BIT;
DECLARE @ID_CONDICION INT;
DECLARE @ID_METODO_PAGO INT;
DECLARE @ID_ENTREGA INT;

-- Variables Detalle
DECLARE @NumProductosEnVenta INT;
DECLARE @j INT;
DECLARE @ID_PRODUCTO INT;
DECLARE @CANTIDAD INT;
DECLARE @PRECIO DECIMAL(9,2);
DECLARE @ITBIS DECIMAL(9,2);

-- Secuenciadores simulados (Basados en tu imagen)
-- E31 comienza por el 37,301 (ejemplo imagen)
-- E32 comienza por 1,000,000 (ejemplo imagen)
DECLARE @SeqE31 BIGINT = 37301;
DECLARE @SeqE32 BIGINT = 1000000;
DECLARE @SeqE44 BIGINT = 76;
DECLARE @SeqE45 BIGINT = 200;

WHILE @i < @CantidadVentas
BEGIN
    -- A. Fecha y Hora Aleatoria
    SET @BaseFecha = DATEADD(day, CAST(RAND() * (DATEDIFF(day, @FechaInicio, @FechaFin) + 1) AS INT), @FechaInicio);
    SET @FechaVenta = DATEADD(minute, CAST(RAND() * 1440 AS INT), CAST(@BaseFecha AS DATETIME));
    
    -- B. Seleccionar Actores
    SELECT TOP 1 @ID_VENDEDOR = ID_VENDEDOR FROM VENDEDOR ORDER BY NEWID();
    SELECT TOP 1 @ID_CLIENTE = ID_CLIENTE, @TipoCliente = TIPO_PERSONA, @ID_REGION = id_region, @TieneCredito = TIENE_CREDITO_APROBADO 
    FROM CLIENTE ORDER BY NEWID();

    IF @ID_CLIENTE IS NOT NULL 
    BEGIN
        -- C. Lógica NCF Electrónico (Serie E)
        -- Prioridad: Gubernamental -> Regimen Especial -> Fiscal -> Consumo
        
        DECLARE @Probabilidad FLOAT = RAND();
        
        -- Lógica: 
        -- Si es Jurídica, 70% E31, 10% E44 (Especial), 5% E45 (Gob), 15% E32 (Consumo/Gasto Menor)
        -- Si es Física, 95% E32, 5% E31 (Factura con valor fiscal nombre persona)

        IF @TipoCliente = 'JURIDICA'
        BEGIN
            IF @Probabilidad < 0.05 
            BEGIN
                SET @ID_TIPO_NCF = 4; -- E45 Gubernamental
                SET @SerieNCF = 'E45';
                SET @SecuenciaNCF = @SeqE45;
                SET @SeqE45 = @SeqE45 + 1;
            END
            ELSE IF @Probabilidad < 0.15
            BEGIN
                SET @ID_TIPO_NCF = 3; -- E44 Regimen Especial
                SET @SerieNCF = 'E44';
                SET @SecuenciaNCF = @SeqE44;
                SET @SeqE44 = @SeqE44 + 1;
            END
            ELSE
            BEGIN
                SET @ID_TIPO_NCF = 1; -- E31 Crédito Fiscal
                SET @SerieNCF = 'E31';
                SET @SecuenciaNCF = @SeqE31;
                SET @SeqE31 = @SeqE31 + 1;
            END
        END
        ELSE -- Cliente Físico
        BEGIN
            IF @Probabilidad > 0.90 -- A veces una persona física pide factura fiscal
            BEGIN
                SET @ID_TIPO_NCF = 1; -- E31
                SET @SerieNCF = 'E31';
                SET @SecuenciaNCF = @SeqE31;
                SET @SeqE31 = @SeqE31 + 1;
            END
            ELSE
            BEGIN
                SET @ID_TIPO_NCF = 2; -- E32 Consumo
                SET @SerieNCF = 'E32';
                SET @SecuenciaNCF = @SeqE32;
                SET @SeqE32 = @SeqE32 + 1;
            END
        END

        -- Formato e-CF: Serie (3 chars) + Secuencia (10 dígitos generalmente para e-CF)
        -- Ejemplo: E310000037301
        SET @NCF_Full = @SerieNCF + RIGHT('0000000000' + CAST(@SecuenciaNCF AS VARCHAR(20)), 10);

        -- D. Condición de Pago
        IF @TieneCredito = 1 AND RAND() > 0.6
        BEGIN
            SET @ID_CONDICION = 3; -- Crédito
            SET @ID_METODO_PAGO = 4; -- Cheque
        END
        ELSE
        BEGIN
            SET @ID_CONDICION = 1; -- Contado
            SELECT TOP 1 @ID_METODO_PAGO = ID_METODO FROM METODO_PAGO WHERE ID_METODO IN (1,2,3) ORDER BY NEWID();
        END

        -- E. Método de Entrega
        IF @ID_METODO_PAGO IN (2,3) AND RAND() > 0.4
            SELECT TOP 1 @ID_ENTREGA = ID_ENTREGA FROM METODO_ENTREGA WHERE ES_ONLINE = 1 ORDER BY NEWID();
        ELSE
            SET @ID_ENTREGA = 1; -- Tienda

        -- F. Insertar Cabecera Venta
        INSERT INTO VENTAS (
            FECHA, ID_CLIENTE, ID_VENDEDOR, ID_REGION, 
            ID_CONDICION, ID_METODO_PAGO, ID_ENTREGA, 
            ID_TIPO_NCF, NCF_GENERADO
        )
        VALUES (
            @FechaVenta, @ID_CLIENTE, @ID_VENDEDOR, @ID_REGION, 
            @ID_CONDICION, @ID_METODO_PAGO, @ID_ENTREGA, 
            @ID_TIPO_NCF, @NCF_Full
        );

        SET @NuevaVentaID = SCOPE_IDENTITY();

        -- G. Insertar Detalle
        SET @NumProductosEnVenta = FLOOR(RAND() * (10 - 1 + 1) + 1);
        SET @j = 0;

        WHILE @j < @NumProductosEnVenta
        BEGIN
            SELECT TOP 1 @ID_PRODUCTO = ID_PRODUCTO, @PRECIO = PRECIO_VENTA 
            FROM PRODUCTO ORDER BY NEWID();

            SET @CANTIDAD = FLOOR(RAND() * (10 - 1 + 1) + 1);
            SET @ITBIS = (@PRECIO * @CANTIDAD) * 0.18; -- ITBIS 18%

            INSERT INTO DETALLE_VENTAS (ID_VENTA, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO, ITBIS_UNITARIO, SUBTOTAL)
            VALUES (@NuevaVentaID, @ID_PRODUCTO, @CANTIDAD, @PRECIO, (@PRECIO * 0.18), (@CANTIDAD * @PRECIO));

            SET @j = @j + 1;
        END

        -- H. Actualizar Totales
        UPDATE VENTAS
        SET SUBTOTAL_VENTA = (SELECT ISNULL(SUM(SUBTOTAL), 0) FROM DETALLE_VENTAS WHERE ID_VENTA = @NuevaVentaID),
            TOTAL_ITBIS = (SELECT ISNULL(SUM(ITBIS_UNITARIO * CANTIDAD), 0) FROM DETALLE_VENTAS WHERE ID_VENTA = @NuevaVentaID)
        WHERE ID_VENTA = @NuevaVentaID;

        UPDATE VENTAS
        SET TOTAL_VENTA = SUBTOTAL_VENTA + TOTAL_ITBIS
        WHERE ID_VENTA = @NuevaVentaID;
        
        SET @i = @i + 1;
    END
END
GO



-- 5. VISTA ANALÍTICA AVANZADA (ADAPTADA A RD)
CREATE OR ALTER VIEW VISTA_ANALITICA_DETALLADA AS
SELECT 
    -- Identificadores y Tiempo
    V.ID_VENTA AS ID_PEDIDO,
    DV.ID_DETALLE,
    V.FECHA,
    YEAR(V.FECHA) AS Anio,
    MONTH(V.FECHA) AS Mes,
    
    -- Cliente
    V.ID_CLIENTE,
    CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE) AS Cliente,
    C.RNC_CEDULA,
    C.TIPO_PERSONA,
    
    -- Datos Fiscales y Pago
    TN.CODIGO_INTERNO AS TIPO_NCF_CODIGO, -- 31 o 32
    TN.DESCRIPCION AS TIPO_COMPROBANTE,
    V.NCF_GENERADO,
    CP.NOMBRE_CONDICION AS Condicion_Pago,
    MP.METODO AS Metodo_Pago,
    
    -- Logística
    ME.TIPO_ENTREGA,
    CASE WHEN ME.ES_ONLINE = 1 THEN 'Online' ELSE 'Tienda Física' END AS Canal_Venta,
    
    -- Vendedor y Ubicación
    VD.VENDEDOR AS Nombre_Vendedor,
    VD.SUCURSAL,
    P.nombreProvincia AS Provincia,
    R.REGION AS Region,
    
    -- Producto
    PR.PRODUCTO AS Nombre_Producto,
    
    -- Métricas Financieras (Con desglose ITBIS)
    DV.CANTIDAD,
    CAST(DV.PRECIO_UNITARIO AS DECIMAL(18,2)) AS PRECIO_VENTA_SIN_ITBIS,
    CAST(PR.PRECIO_COMPRA AS DECIMAL(18,2)) AS COSTO_UNITARIO,
    
    CAST(DV.SUBTOTAL AS DECIMAL(18,2)) AS VENTA_NETA, -- Sin impuestos
    CAST((DV.ITBIS_UNITARIO * DV.CANTIDAD) AS DECIMAL(18,2)) AS ITBIS_TOTAL,
    CAST(DV.SUBTOTAL + (DV.ITBIS_UNITARIO * DV.CANTIDAD) AS DECIMAL(18,2)) AS VENTA_BRUTA, -- Con impuestos
    
    CAST(DV.SUBTOTAL - (DV.CANTIDAD * PR.PRECIO_COMPRA) AS DECIMAL(18,2)) AS MARGEN_BENEFICIO,
    
    -- Fotos
    ISNULL(FP.foto_Productos_url, 'N/A') AS foto_Productos_url,
    ISNULL(FV.foto_Vendedor_url, 'N/A') AS foto_Vendedor_url

FROM VENTAS V
INNER JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA
INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
INNER JOIN VENDEDOR VD ON V.ID_VENDEDOR = VD.ID_VENDEDOR
INNER JOIN PROVINCIAS P ON VD.PROVINCIA = P.id_provincia
INNER JOIN REGION R ON P.id_region = R.ID_REGION
INNER JOIN PRODUCTO PR ON DV.ID_PRODUCTO = PR.ID_PRODUCTO
INNER JOIN TIPO_NCF TN ON V.ID_TIPO_NCF = TN.ID_TIPO_NCF
INNER JOIN CONDICION_PAGO CP ON V.ID_CONDICION = CP.ID_CONDICION
INNER JOIN METODO_PAGO MP ON V.ID_METODO_PAGO = MP.ID_METODO
INNER JOIN METODO_ENTREGA ME ON V.ID_ENTREGA = ME.ID_ENTREGA
LEFT JOIN FOTO_PRODUCTOS FP ON PR.ID_PRODUCTO = FP.ID_PRODUCTO
LEFT JOIN FOTOS_VENDEDOR FV ON VD.ID_VENDEDOR = FV.ID_VENDEDOR;
GO


-- 4. CONSULTAR RESULTADOS
SELECT TOP 2000 
    ID_PEDIDO, 
    FECHA, 
    Cliente, 
    RNC_CEDULA, 
    TIPO_COMPROBANTE, -- Ahora dirá "Electrónica"
    NCF_GENERADO,     -- Ahora verás E31..., E32...
    VENTA_BRUTA 
FROM VISTA_ANALITICA_DETALLADA 
ORDER BY NCF_GENERADO DESC; -- Ordenar por NCF para ver la secuencia





-- 6. VERIFICACIÓN FINAL
SELECT TOP 50 
    ID_PEDIDO, FECHA, Cliente, RNC_CEDULA, TIPO_COMPROBANTE, NCF_GENERADO, 
    Condicion_Pago, Canal_Venta, Nombre_Producto, VENTA_BRUTA 
FROM VISTA_ANALITICA_DETALLADA 
ORDER BY FECHA DESC;



USE SUPERMERCADO_JPV_V6;
GO

SELECT 
    TN.SERIE_NCF,
    TN.DESCRIPCION,
    COUNT(V.ID_VENTA) AS Cantidad_Facturas,
    FORMAT(SUM(V.TOTAL_VENTA), 'N2') AS Total_Dinero_Vendido,
    -- Calcula el porcentaje del total de facturas
    CAST(COUNT(V.ID_VENTA) * 100.0 / (SELECT COUNT(*) FROM VENTAS) AS DECIMAL(5,2)) AS Porcentaje_Del_Total
FROM VENTAS V
INNER JOIN TIPO_NCF TN ON V.ID_TIPO_NCF = TN.ID_TIPO_NCF
GROUP BY TN.SERIE_NCF, TN.DESCRIPCION
ORDER BY TN.SERIE_NCF;


SELECT 
    C.TIPO_PERSONA,
    COUNT(V.ID_VENTA) AS Cantidad_Compras,
    FORMAT(SUM(V.TOTAL_VENTA), 'N2') AS Total_Comprado
FROM VENTAS V
INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
GROUP BY C.TIPO_PERSONA;


SELECT 
    MP.METODO AS Metodo_Pago,
    ME.TIPO_ENTREGA AS Entrega,
    COUNT(V.ID_VENTA) AS Cantidad
FROM VENTAS V
INNER JOIN METODO_PAGO MP ON V.ID_METODO_PAGO = MP.ID_METODO
INNER JOIN METODO_ENTREGA ME ON V.ID_ENTREGA = ME.ID_ENTREGA
GROUP BY MP.METODO, ME.TIPO_ENTREGA
ORDER BY MP.METODO, Cantidad DESC;



USE SUPERMERCADO_JPV_V6;
GO

-- 5. CREACIÓN DE LA VISTA COMPLETA (ACTUALIZADA V6)

CREATE OR ALTER VIEW VISTA_COMPLETA_VENTAS AS
SELECT 
    V.ID_VENTA AS ID_PEDIDO,
    DV.ID_DETALLE,
    V.FECHA,
    
    -- CLIENTE (Nuevos campos Fiscales)
    V.ID_CLIENTE,
    CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE) AS Cliente,
    C.RNC_CEDULA,
    C.TIPO_PERSONA,

    -- DATOS FISCALES Y DE PAGO (NUEVO)
    TN.SERIE_NCF AS Serie_Comprobante,
    TN.DESCRIPCION AS Tipo_Comprobante,
    V.NCF_GENERADO,
    CP.NOMBRE_CONDICION AS Condicion_Pago,
    MP.METODO AS Metodo_Pago,
    
    -- LOGÍSTICA (NUEVO)
    ME.TIPO_ENTREGA,
    CASE WHEN ME.ES_ONLINE = 1 THEN 'Si' ELSE 'No' END AS Es_Online,

    -- VENDEDOR
    V.ID_VENDEDOR,
    VD.VENDEDOR AS VENDEDOR,
    G.Genero AS Genero_Vendedor,
    VD.SUCURSAL AS Sucursal_Vendedor,
    P.nombreProvincia AS Provincia_Vendedor,
    P.latitud,
    P.longitud,
    R.REGION AS Region_Vendedor,

    -- PRODUCTO Y FINANZAS (DESDE DETALLE)
    DV.ID_PRODUCTO,
    PR.PRODUCTO AS Nombre_Producto,
    PR.PRECIO_COMPRA AS Costo_Unitario,
    DV.PRECIO_UNITARIO AS Precio_Venta, 
    DV.CANTIDAD,
    
    -- CALCULOS CON ITBIS
    DV.SUBTOTAL AS Venta_Neta, -- (Cantidad * Precio)
    (DV.ITBIS_UNITARIO * DV.CANTIDAD) AS Total_Impuesto,
    (DV.SUBTOTAL + (DV.ITBIS_UNITARIO * DV.CANTIDAD)) AS Venta_Total_Bruta, -- (Neto + Impuesto)

    -- FOTOS
    ISNULL(FP.foto_Productos_url, 'N/A') AS foto_Productos_url,
    ISNULL(FV.foto_Vendedor_url, 'N/A') AS foto_Vendedor_url

FROM VENTAS V
INNER JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA 
INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
INNER JOIN VENDEDOR VD ON V.ID_VENDEDOR = VD.ID_VENDEDOR
INNER JOIN Genero G ON VD.id_genero = G.ID_Genero
INNER JOIN PROVINCIAS P ON VD.PROVINCIA = P.id_provincia
INNER JOIN REGION R ON P.id_region = R.ID_REGION
INNER JOIN PRODUCTO PR ON DV.ID_PRODUCTO = PR.ID_PRODUCTO
-- NUEVOS JOINS
INNER JOIN TIPO_NCF TN ON V.ID_TIPO_NCF = TN.ID_TIPO_NCF
INNER JOIN CONDICION_PAGO CP ON V.ID_CONDICION = CP.ID_CONDICION
INNER JOIN METODO_PAGO MP ON V.ID_METODO_PAGO = MP.ID_METODO
INNER JOIN METODO_ENTREGA ME ON V.ID_ENTREGA = ME.ID_ENTREGA
LEFT JOIN FOTO_PRODUCTOS FP ON PR.ID_PRODUCTO = FP.ID_PRODUCTO
LEFT JOIN FOTOS_VENDEDOR FV ON VD.ID_VENDEDOR = FV.ID_VENDEDOR;
GO

-- Verificación rápida
SELECT TOP 10 * FROM VISTA_COMPLETA_VENTAS;
GO

-- 2. CÁLCULO DE TOTALES (KPIs) ACTUALIZADOS
SELECT 
    -- Ingreso sin impuestos (Lo que realmente gana la empresa bruto)
    SUM(VCV.Venta_Neta) AS Ingreso_Neto_Total,
    
    -- Total cobrado al cliente (Incluye impuestos)
    SUM(VCV.Venta_Total_Bruta) AS Ingreso_Bruto_Total,
    
    -- Impuestos recaudados para la DGII
    SUM(VCV.Total_Impuesto) AS Total_ITBIS_Recaudado,
    
    SUM(VCV.CANTIDAD) AS Cantidad_Total,
    
    -- Costo = Precio Compra * Cantidad
    SUM(CAST(VCV.Costo_Unitario AS DECIMAL(12,2)) * VCV.CANTIDAD) AS Costo_Total,
    
    -- Margen = Venta Neta - Costo Total (El ITBIS no es ganancia, se excluye del margen)
    SUM(VCV.Venta_Neta - (CAST(VCV.Costo_Unitario AS DECIMAL(12,2)) * VCV.CANTIDAD)) AS Margen_Total,
    
    -- Porcentaje Margen Global
    CASE 
        WHEN SUM(VCV.Venta_Neta) = 0 THEN 0
        ELSE 
            (SUM(VCV.Venta_Neta - (CAST(VCV.Costo_Unitario AS DECIMAL(12,2)) * VCV.CANTIDAD)) / 
             SUM(VCV.Venta_Neta)) * 100
    END AS Porcentaje_Margen
FROM VISTA_COMPLETA_VENTAS VCV;
GO

-- 3. RANKINGS (CTEs)

-- Ranking de Clientes (Por Venta Bruta)
WITH Rankings_Clientes AS (
    SELECT 
        VCV.ID_CLIENTE,
        VCV.Cliente,
        VCV.TIPO_PERSONA,
        SUM(VCV.Venta_Total_Bruta) AS Total_Comprado,
        RANK() OVER (ORDER BY SUM(VCV.Venta_Total_Bruta) DESC) AS Ranking_Cliente
    FROM VISTA_COMPLETA_VENTAS VCV
    GROUP BY VCV.ID_CLIENTE, VCV.Cliente, VCV.TIPO_PERSONA
)
SELECT TOP 10 * FROM Rankings_Clientes;
GO

-- Ranking de Vendedores
WITH Rankings_Vendedores AS (
    SELECT 
        VCV.ID_VENDEDOR,
        VCV.VENDEDOR,
        SUM(VCV.Venta_Neta) AS Total_Vendido_Neto, -- Vendedores suelen comisionar sobre el neto (sin impuestos)
        RANK() OVER (ORDER BY SUM(VCV.Venta_Neta) DESC) AS Ranking_Vendedor
    FROM VISTA_COMPLETA_VENTAS VCV
    GROUP BY VCV.ID_VENDEDOR, VCV.VENDEDOR
)
SELECT * FROM Rankings_Vendedores;
GO

-- Ranking de Productos
WITH Rankings_Productos AS (
    SELECT 
        VCV.ID_PRODUCTO,
        VCV.Nombre_Producto AS Producto,
        SUM(VCV.CANTIDAD) AS Unidades_Vendidas,
        SUM(VCV.Venta_Total_Bruta) AS Ingreso_Generado,
        RANK() OVER (ORDER BY SUM(VCV.Venta_Total_Bruta) DESC) AS Ranking_Producto
    FROM VISTA_COMPLETA_VENTAS VCV
    GROUP BY VCV.ID_PRODUCTO, VCV.Nombre_Producto 
)
SELECT TOP 10 * FROM Rankings_Productos;
GO

-- 4. VISTA ANALÍTICA AVANZADA (CON DATOS DGII, LOGÍSTICA Y CRÉDITO)
CREATE OR ALTER VIEW VISTA_ANALITICA_DETALLADA AS
SELECT 
    -- Identificadores
    V.ID_VENTA AS ID_PEDIDO,
    DV.ID_DETALLE,
    V.FECHA,
    YEAR(V.FECHA) AS Anio,
    MONTH(V.FECHA) AS Mes,
    DATENAME(MONTH, V.FECHA) AS Nombre_Mes,
    
    -- Datos Cliente
    V.ID_CLIENTE,
    CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE) AS Cliente,
    C.RNC_CEDULA,
    C.TIPO_PERSONA,
    
    -- Datos Fiscales (DGII Rep. Dom.)
    TN.CODIGO_INTERNO,
    TN.SERIE_NCF,
    TN.DESCRIPCION AS Tipo_Comprobante,
    V.NCF_GENERADO,
    
    -- Datos de Pago y Entrega
    CP.NOMBRE_CONDICION AS Condicion_Pago,
    CASE WHEN CP.ES_CREDITO = 1 THEN 'Crédito' ELSE 'Contado' END AS Tipo_Venta_Financiera,
    MP.METODO AS Metodo_Pago,
    ME.TIPO_ENTREGA,
    CASE WHEN ME.ES_ONLINE = 1 THEN 'Online' ELSE 'Física' END AS Canal_Venta,

    -- Datos Vendedor y Ubicación Geográfica
    V.ID_VENDEDOR,
    VD.VENDEDOR AS Nombre_Vendedor,
    G.Genero AS Genero_Vendedor,
    VD.SUCURSAL,
    P.nombreProvincia AS Provincia_Vendedor,
    R.REGION AS Region_Vendedor,
    P.latitud,
    P.longitud,
    
    -- Datos Producto
    DV.ID_PRODUCTO,
    PR.PRODUCTO AS Nombre_Producto,
    
    -- Métricas Base
    DV.CANTIDAD,
    CAST(DV.PRECIO_UNITARIO AS DECIMAL(18,2)) AS PRECIO_VENTA_UNITARIO,
    CAST(PR.PRECIO_COMPRA AS DECIMAL(18,2)) AS COSTO_UNITARIO,
    CAST(DV.ITBIS_UNITARIO AS DECIMAL(18,2)) AS ITBIS_UNITARIO,
    
    -- Cálculos de Línea Financieros
    CAST(DV.SUBTOTAL AS DECIMAL(18,2)) AS VENTA_NETA, -- Base imponible
    CAST((DV.ITBIS_UNITARIO * DV.CANTIDAD) AS DECIMAL(18,2)) AS TOTAL_ITBIS, -- Impuesto
    CAST((DV.SUBTOTAL + (DV.ITBIS_UNITARIO * DV.CANTIDAD)) AS DECIMAL(18,2)) AS VENTA_BRUTA, -- Total a pagar
    
    CAST(DV.CANTIDAD * PR.PRECIO_COMPRA AS DECIMAL(18,2)) AS COSTO_TOTAL,
    
    -- Margen (Venta Neta - Costo)
    CAST(DV.SUBTOTAL - (DV.CANTIDAD * PR.PRECIO_COMPRA) AS DECIMAL(18,2)) AS MARGEN_BENEFICIO,
    
    -- Porcentaje de Margen
    CAST(
        CASE 
            WHEN DV.SUBTOTAL = 0 THEN 0
            ELSE ((DV.SUBTOTAL - (DV.CANTIDAD * PR.PRECIO_COMPRA)) / NULLIF(DV.SUBTOTAL, 0)) * 100 
        END 
    AS DECIMAL(7,2)) AS PORCENTAJE_MARGEN,

    -- Ranking por cliente
    RANK() OVER (PARTITION BY V.ID_CLIENTE ORDER BY DV.SUBTOTAL DESC) AS RANK_PRODUCTO_EN_HISTORIAL_CLIENTE,
    
    -- Fotos
    ISNULL(FP.foto_Productos_url, 'N/A') AS foto_Productos_url,
    ISNULL(FV.foto_Vendedor_url, 'N/A') AS foto_Vendedor_url

FROM VENTAS V
INNER JOIN DETALLE_VENTAS DV ON V.ID_VENTA = DV.ID_VENTA
INNER JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
INNER JOIN VENDEDOR VD ON V.ID_VENDEDOR = VD.ID_VENDEDOR
LEFT JOIN Genero G ON VD.id_genero = G.ID_Genero
INNER JOIN PROVINCIAS P ON VD.PROVINCIA = P.id_provincia
INNER JOIN REGION R ON P.id_region = R.ID_REGION
INNER JOIN PRODUCTO PR ON DV.ID_PRODUCTO = PR.ID_PRODUCTO
-- JOINS NUEVOS PARA V6
INNER JOIN TIPO_NCF TN ON V.ID_TIPO_NCF = TN.ID_TIPO_NCF
INNER JOIN CONDICION_PAGO CP ON V.ID_CONDICION = CP.ID_CONDICION
INNER JOIN METODO_PAGO MP ON V.ID_METODO_PAGO = MP.ID_METODO
INNER JOIN METODO_ENTREGA ME ON V.ID_ENTREGA = ME.ID_ENTREGA
LEFT JOIN FOTO_PRODUCTOS FP ON PR.ID_PRODUCTO = FP.ID_PRODUCTO
LEFT JOIN FOTOS_VENDEDOR FV ON VD.ID_VENDEDOR = FV.ID_VENDEDOR;
GO

-- Consulta de prueba final para verificar los nuevos campos
SELECT TOP 100 
    ID_PEDIDO, 
    FECHA, 
    Cliente, 
    RNC_CEDULA, 
    NCF_GENERADO, 
    Tipo_Comprobante, 
    Condicion_Pago, 
    Canal_Venta, 
    Nombre_Producto, 
    VENTA_NETA, 
    TOTAL_ITBIS, 
    VENTA_BRUTA 
FROM VISTA_ANALITICA_DETALLADA 
ORDER BY FECHA DESC, ID_PEDIDO DESC;
GO

SELECT * FROM VISTA_ANALITICA_DETALLADA


-- CONSULTAS BASICAS A LAS TABLAS (SIN CAMBIOS, SOLO PARA VALIDAR)
select * from USUARIOS;
select * from CLIENTE;
select * from VENDEDOR;
select * from PRODUCTO;
select * from FOTO_PRODUCTOS;
select * from VENTAS;
select * from DETALLE_VENTAS;





USE SUPERMERCADO_JPV_V6;
GO

-- 1. TABLA DE AUDITORÍA (CAJA NEGRA)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TABLA_AUDITORIA')
BEGIN
    CREATE TABLE TABLA_AUDITORIA (
        ID_AUDITORIA INT PRIMARY KEY IDENTITY(1,1),
        FECHA DATETIME DEFAULT GETDATE(),
        USUARIO_DB VARCHAR(100),
        TABLA_AFECTADA VARCHAR(50),
        ACCION VARCHAR(20), -- INSERT, UPDATE, DELETE
        DATOS_ANTERIORES XML NULL, -- Guardamos el estado previo en formato XML
        DATOS_NUEVOS XML NULL      -- Guardamos el nuevo estado
    );
END
GO

-- 2. TRIGGER DE VALIDACIÓN DE STOCK (CRÍTICO)
-- Este trigger se dispara ANTES de que se inserte una venta.
-- Si no hay stock, CANCELA la operación y devuelve un mensaje de error.

CREATE OR ALTER TRIGGER TRG_VALIDAR_STOCK_VENTA
ON DETALLE_VENTAS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Verificar si algún producto insertado excede el stock disponible
    IF EXISTS (
        SELECT 1
        FROM inserted i
        INNER JOIN PRODUCTO p ON i.ID_PRODUCTO = p.ID_PRODUCTO
        WHERE p.STOCK < i.CANTIDAD
    )
    BEGIN
        -- Obtener el nombre del producto que falló para el mensaje
        DECLARE @NombreProducto VARCHAR(100);
        DECLARE @StockActual INT;
        DECLARE @CantidadSolicitada INT;

        SELECT TOP 1 
            @NombreProducto = p.PRODUCTO, 
            @StockActual = p.STOCK,
            @CantidadSolicitada = i.CANTIDAD
        FROM inserted i
        INNER JOIN PRODUCTO p ON i.ID_PRODUCTO = p.ID_PRODUCTO
        WHERE p.STOCK < i.CANTIDAD;

        -- Cancelar la transacción
        ROLLBACK TRANSACTION;

        -- Lanzar mensaje de error personalizado
        RAISERROR ('ERROR CRÍTICO DE INVENTARIO: No se puede facturar el producto "%s". Stock Actual: %d, Solicitado: %d.', 16, 1, @NombreProducto, @StockActual, @CantidadSolicitada);
        RETURN;
    END

    -- Si hay stock, descontamos automáticamente del inventario
    UPDATE p
    SET p.STOCK = p.STOCK - i.CANTIDAD
    FROM PRODUCTO p
    INNER JOIN inserted i ON p.ID_PRODUCTO = i.ID_PRODUCTO;
END
GO

-- 3. TRIGGER DE AUDITORÍA (Ejemplo en PRODUCTO)
-- Registra cualquier cambio de precio o nombre en la tabla de auditoría.

CREATE OR ALTER TRIGGER TRG_AUDITORIA_PRODUCTO
ON PRODUCTO
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion VARCHAR(20);
    DECLARE @DatosAnt XML;
    DECLARE @DatosNue XML;

    -- Determinar la acción
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    -- Capturar datos en XML
    SET @DatosAnt = (SELECT * FROM deleted FOR XML AUTO);
    SET @DatosNue = (SELECT * FROM inserted FOR XML AUTO);

    INSERT INTO TABLA_AUDITORIA (USUARIO_DB, TABLA_AFECTADA, ACCION, DATOS_ANTERIORES, DATOS_NUEVOS)
    VALUES (SYSTEM_USER, 'PRODUCTO', @Accion, @DatosAnt, @DatosNue);
END
GO

-- 4. PROCEDIMIENTOS ALMACENADOS: CRUD CLIENTES

-- A. CREAR CLIENTE
CREATE OR ALTER PROCEDURE SP_CREAR_CLIENTE
    @Nombre VARCHAR(100),
    @Apellido VARCHAR(100),
    @RNC_Cedula VARCHAR(20),
    @TipoPersona VARCHAR(20), -- 'FISICA' o 'JURIDICA'
    @Region INT,
    @Provincia INT,
    @Direccion VARCHAR(200),
    @TieneCredito BIT,
    @LimiteCredito DECIMAL(12,2)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Validación simple de duplicados
    IF EXISTS (SELECT 1 FROM CLIENTE WHERE RNC_CEDULA = @RNC_Cedula)
    BEGIN
        RAISERROR('El Cliente con RNC/Cédula %s ya existe.', 16, 1, @RNC_Cedula);
        RETURN;
    END

    -- Insertar el ID manualmente (o usar identity si modificas la tabla)
    DECLARE @NewID INT = (SELECT ISNULL(MAX(ID_CLIENTE),0) + 1 FROM CLIENTE);

    INSERT INTO CLIENTE (ID_CLIENTE, NOMBRE_CLIENTE, APELLIDO_CLIENTE, RNC_CEDULA, TIPO_PERSONA, id_region, id_provincia, DIRECCION, TIENE_CREDITO_APROBADO, LIMITE_CREDITO)
    VALUES (@NewID, @Nombre, @Apellido, @RNC_Cedula, @TipoPersona, @Region, @Provincia, @Direccion, @TieneCredito, @LimiteCredito);

    PRINT 'Cliente creado exitosamente con ID: ' + CAST(@NewID AS VARCHAR);
END
GO

-- B. ACTUALIZAR CLIENTE
CREATE OR ALTER PROCEDURE SP_ACTUALIZAR_CLIENTE
    @ID_Cliente INT,
    @Direccion VARCHAR(200),
    @LimiteCredito DECIMAL(12,2)
AS
BEGIN
    UPDATE CLIENTE 
    SET DIRECCION = @Direccion, 
        LIMITE_CREDITO = @LimiteCredito,
        fecha_actualizacion = GETDATE()
    WHERE ID_CLIENTE = @ID_Cliente;
END
GO

-- 5. PROCEDIMIENTO MAESTRO: PROCESAR FACTURACIÓN
-- Este SP es el cerebro del sistema. Maneja Stock, NCF y Ventas.

CREATE OR ALTER PROCEDURE SP_FACTURAR_VENTA
    @ID_Cliente INT,
    @ID_Vendedor INT,
    @ID_Producto INT, -- Simplificado para 1 producto (en app real usarías JSON o tabla temporal para varios)
    @Cantidad INT,
    @ID_MetodoPago INT,
    @ID_Entrega INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. Validar Existencia (Doble validación: Aquí y en el Trigger)
        DECLARE @Stock INT, @Precio DECIMAL(9,2), @NombreProd VARCHAR(100);
        SELECT @Stock = STOCK, @Precio = PRECIO_VENTA, @NombreProd = PRODUCTO 
        FROM PRODUCTO WHERE ID_PRODUCTO = @ID_Producto;

        IF @Stock < @Cantidad
        BEGIN
            RAISERROR('Stock insuficiente para el producto %s. Disponible: %d', 16, 1, @NombreProd, @Stock);
        END

        -- 2. Obtener Datos del Cliente para NCF
        DECLARE @TipoPersona VARCHAR(20), @Region INT;
        SELECT @TipoPersona = TIPO_PERSONA, @Region = id_region 
        FROM CLIENTE WHERE ID_CLIENTE = @ID_Cliente;

        -- 3. Lógica de NCF (Serie E)
        DECLARE @ID_TipoNCF INT, @SerieNCF VARCHAR(3), @NCF_Generado VARCHAR(19);
        
        -- Lógica simple: Jurídica -> E31, Física -> E32
        IF @TipoPersona = 'JURIDICA'
        BEGIN
            SET @ID_TipoNCF = 1; -- E31
            SET @SerieNCF = 'E31';
        END
        ELSE
        BEGIN
            SET @ID_TipoNCF = 2; -- E32
            SET @SerieNCF = 'E32';
        END
        
        -- Generar Secuencia Aleatoria (En prod usar SEQUENCE object)
        SET @NCF_Generado = @SerieNCF + RIGHT('0000000000' + CAST(ABS(CHECKSUM(NEWID())) % 10000000 AS VARCHAR), 10);

        -- 4. Cálculos
        DECLARE @ITBIS_Unitario DECIMAL(9,2) = @Precio * 0.18;
        DECLARE @SubTotal DECIMAL(12,2) = @Cantidad * @Precio;
        DECLARE @TotalImpuesto DECIMAL(12,2) = @Cantidad * @ITBIS_Unitario;
        DECLARE @TotalVenta DECIMAL(12,2) = @SubTotal + @TotalImpuesto;

        -- 5. Insertar Cabecera Venta
        INSERT INTO VENTAS (FECHA, ID_CLIENTE, ID_VENDEDOR, ID_REGION, ID_CONDICION, ID_METODO_PAGO, ID_ENTREGA, ID_TIPO_NCF, NCF_GENERADO, SUBTOTAL_VENTA, TOTAL_ITBIS, TOTAL_VENTA, ESTADO)
        VALUES (GETDATE(), @ID_Cliente, @ID_Vendedor, @Region, 1, @ID_MetodoPago, @ID_Entrega, @ID_TipoNCF, @NCF_Generado, @SubTotal, @TotalImpuesto, @TotalVenta, 'COMPLETADA');

        DECLARE @NewVentaID INT = SCOPE_IDENTITY();

        -- 6. Insertar Detalle (Esto disparará el TRIGGER TRG_VALIDAR_STOCK_VENTA)
        INSERT INTO DETALLE_VENTAS (ID_VENTA, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO, ITBIS_UNITARIO, SUBTOTAL)
        VALUES (@NewVentaID, @ID_Producto, @Cantidad, @Precio, @ITBIS_Unitario, @SubTotal);

        COMMIT TRANSACTION;
        
        PRINT 'Venta Exitosa. Factura #' + CAST(@NewVentaID AS VARCHAR) + ' NCF: ' + @NCF_Generado;
    
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR ('Error al procesar la venta: %s', 16, 1, @ErrorMessage);
    END CATCH
END
GO

-- 6. EJEMPLOS DE PRUEBA (VALIDACIONES)

-- Prueba 1: Intentar vender algo con stock (Debe funcionar)
-- Asumiendo Producto 1 tiene stock
EXEC SP_FACTURAR_VENTA 
    @ID_Cliente = 1, 
    @ID_Vendedor = 1, 
    @ID_Producto = 1, 
    @Cantidad = 2, 
    @ID_MetodoPago = 1, 
    @ID_Entrega = 1;
GO

-- Prueba 2: Intentar vender MÁS de lo que hay (Debe fallar y dar mensaje)
-- Pongamos una cantidad absurda
EXEC SP_FACTURAR_VENTA 
    @ID_Cliente = 1, 
    @ID_Vendedor = 1, 
    @ID_Producto = 1, 
    @Cantidad = 50000, -- Imposible tener tanto stock
    @ID_MetodoPago = 1, 
    @ID_Entrega = 1;
GO

-- Prueba 3: Ver Auditoría después de los cambios
SELECT * FROM TABLA_AUDITORIA ORDER BY FECHA DESC;
GO

-- Prueba 4: Ver cómo bajó el stock del producto 1
SELECT ID_PRODUCTO, PRODUCTO, STOCK FROM PRODUCTO WHERE ID_PRODUCTO = 1;
GO
```

---
## 10. 🤝 Contribucion
1. Fork el proyecto.
2. Crear rama.

*Generado el 2026-01-15*
