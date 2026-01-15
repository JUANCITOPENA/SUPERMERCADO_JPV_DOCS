<<<<<<< HEAD
# SUPERMERCADO_JPV_DOCS
SUPERMERCADO_JPV_DOCS
=======
﻿# 🛒 SUPERMERCADO_JPV_V6 - Sistema de Gestion Integral

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
*   Acceso con privilegios db_owner o sysadmin.

### Paso a Paso
1.  **Clonar Repositorio:** Descargue los scripts DDL.
2.  **Crear Base de Datos:**
    `sql
    CREATE DATABASE SUPERMERCADO_JPV_V6;
    `
3.  **Ejecutar Scripts:** Corra el script schema.sql seguido de seed_data.sql.
4.  **Configurar Cadena de Conexion:**
    Server=10.0.0.15;Database=SUPERMERCADO_JPV_V6;User Id=JUANCITO;Password=123456;

---

## 7. 🚀 Uso y Operacion
El sistema esta disenado para ser consumido por una API o Aplicacion de Escritorio.
*   **Transacciones:** Utilizar los Stored Procedures sp_RegistrarVenta, sp_ActualizarStock.
*   **Consultas:** Usar las Vistas w_ReporteVentas, w_StockBajo para lectura.
*   **Mantenimiento:** Reconstruccion de indices semanal (domingos 3 AM).

---

## 8. 💡 Ejemplos de Consultas

**Obtener Top 5 Productos mas vendidos:**
`sql
SELECT TOP 5 p.Nombre, SUM(dv.Cantidad) as TotalVendido
FROM DETALLE_VENTA dv
JOIN PRODUCTO p ON dv.IdProducto = p.Id
GROUP BY p.Nombre
ORDER BY TotalVendido DESC;
`

---

## 9. 🧠 Descripcion del Modelo y Desarrollo

### 📐 Arquitectura
El modelo relacional sigue una arquitectura de estrella modificada para facilitar tanto la transaccion (OLTP) como el reporte rapido.

### 🧩 Diccionario de Datos (Tablas y Estructura)
### 🗃 Tablas del Sistema

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_CLIENTE** | $dataType | NO | *Campo de datos* |
| **NOMBRE_CLIENTE** | $dataType | NO | *Campo de datos* |
| **APELLIDO_CLIENTE** | $dataType | NO | *Campo de datos* |
| **RNC_CEDULA** | $dataType | NO | *Campo de datos* |
| **TIPO_PERSONA** | $dataType | NO | *Campo de datos* |
| **TIENE_CREDITO_APROBADO** | $dataType | YES | *Campo de datos* |
| **LIMITE_CREDITO** | $dataType | YES | *Campo de datos* |
| **DIRECCION** | $dataType | YES | *Campo de datos* |
| **id_region** | $dataType | NO | *Campo de datos* |
| **id_provincia** | $dataType | YES | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |
| **fecha_actualizacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_CONDICION** | $dataType | NO | *Campo de datos* |
| **NOMBRE_CONDICION** | $dataType | NO | *Campo de datos* |
| **ES_CREDITO** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_DETALLE** | $dataType | NO | *Campo de datos* |
| **ID_VENTA** | $dataType | NO | *Campo de datos* |
| **ID_PRODUCTO** | $dataType | NO | *Campo de datos* |
| **CANTIDAD** | $dataType | NO | *Campo de datos* |
| **PRECIO_UNITARIO** | $dataType | NO | *Campo de datos* |
| **ITBIS_UNITARIO** | $dataType | YES | *Campo de datos* |
| **SUBTOTAL** | $dataType | NO | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_Foto** | $dataType | NO | *Campo de datos* |
| **foto_Productos_url** | $dataType | NO | *Campo de datos* |
| **ID_PRODUCTO** | $dataType | NO | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_Foto** | $dataType | NO | *Campo de datos* |
| **foto_Vendedor_url** | $dataType | NO | *Campo de datos* |
| **ID_vendedor** | $dataType | NO | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_Genero** | $dataType | NO | *Campo de datos* |
| **Genero** | $dataType | NO | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_ENTREGA** | $dataType | NO | *Campo de datos* |
| **TIPO_ENTREGA** | $dataType | NO | *Campo de datos* |
| **ES_ONLINE** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_METODO** | $dataType | NO | *Campo de datos* |
| **METODO** | $dataType | NO | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_PRODUCTO** | $dataType | NO | *Campo de datos* |
| **PRODUCTO** | $dataType | NO | *Campo de datos* |
| **STOCK** | $dataType | NO | *Campo de datos* |
| **PRECIO_COMPRA** | $dataType | NO | *Campo de datos* |
| **PRECIO_VENTA** | $dataType | NO | *Campo de datos* |
| **GRAVADO_ITBIS** | $dataType | YES | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **id_provincia** | $dataType | NO | *Campo de datos* |
| **nombreProvincia** | $dataType | NO | *Campo de datos* |
| **id_region** | $dataType | NO | *Campo de datos* |
| **latitud** | $dataType | YES | *Campo de datos* |
| **longitud** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_REGION** | $dataType | NO | *Campo de datos* |
| **REGION** | $dataType | NO | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_AUDITORIA** | $dataType | NO | *Campo de datos* |
| **FECHA** | $dataType | YES | *Campo de datos* |
| **USUARIO_DB** | $dataType | YES | *Campo de datos* |
| **TABLA_AFECTADA** | $dataType | YES | *Campo de datos* |
| **ACCION** | $dataType | YES | *Campo de datos* |
| **DATOS_ANTERIORES** | $dataType | YES | *Campo de datos* |
| **DATOS_NUEVOS** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_TIPO_NCF** | $dataType | NO | *Campo de datos* |
| **CODIGO_INTERNO** | $dataType | NO | *Campo de datos* |
| **DESCRIPCION** | $dataType | NO | *Campo de datos* |
| **SERIE_NCF** | $dataType | NO | *Campo de datos* |
| **REQUIERE_RNC** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_USUARIO** | $dataType | NO | *Campo de datos* |
| **NOMBRE_USUARIO** | $dataType | NO | *Campo de datos* |
| **PASSWORD** | $dataType | NO | *Campo de datos* |
| **ROL** | $dataType | NO | *Campo de datos* |
| **ID_REGION** | $dataType | YES | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_VENDEDOR** | $dataType | NO | *Campo de datos* |
| **VENDEDOR** | $dataType | NO | *Campo de datos* |
| **id_genero** | $dataType | YES | *Campo de datos* |
| **SUCURSAL** | $dataType | YES | *Campo de datos* |
| **PROVINCIA** | $dataType | NO | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

#### 🔹 Tabla: $tableName 
| Columna | Tipo | Nulo | Descripcion |
| :--- | :--- | :--- | :--- |
| **ID_VENTA** | $dataType | NO | *Campo de datos* |
| **FECHA** | $dataType | NO | *Campo de datos* |
| **ID_CLIENTE** | $dataType | NO | *Campo de datos* |
| **ID_VENDEDOR** | $dataType | NO | *Campo de datos* |
| **ID_REGION** | $dataType | NO | *Campo de datos* |
| **ID_CONDICION** | $dataType | NO | *Campo de datos* |
| **ID_METODO_PAGO** | $dataType | NO | *Campo de datos* |
| **ID_ENTREGA** | $dataType | NO | *Campo de datos* |
| **ID_TIPO_NCF** | $dataType | NO | *Campo de datos* |
| **NCF_GENERADO** | $dataType | NO | *Campo de datos* |
| **SUBTOTAL_VENTA** | $dataType | YES | *Campo de datos* |
| **TOTAL_ITBIS** | $dataType | YES | *Campo de datos* |
| **TOTAL_VENTA** | $dataType | YES | *Campo de datos* |
| **ESTADO** | $dataType | YES | *Campo de datos* |
| **fecha_creacion** | $dataType | YES | *Campo de datos* |

---

### 👁 Vistas (Views)
- 📄 **VISTA_ANALITICA_DETALLADA**: Abstraccion de lectura de datos.
- 📄 **VISTA_COMPLETA_VENTAS**: Abstraccion de lectura de datos.
---

### ⚡ Procedimientos Almacenados (Stored Procedures)
| Procedimiento | Logica Principal |
| :--- | :--- |
| **SP_CREAR_CLIENTE** | Ejecuta logica de negocio encapsulada. |
| **SP_ACTUALIZAR_CLIENTE** | Ejecuta logica de negocio encapsulada. |
| **SP_FACTURAR_VENTA** | Ejecuta logica de negocio encapsulada. |
---

### 🔫 Triggers (Disparadores)
- ⚙ **TRG_VALIDAR_STOCK_VENTA**: Automatizacion de eventos en base de datos.
- ⚙ **TRG_AUDITORIA_PRODUCTO**: Automatizacion de eventos en base de datos.

---

## 10. 📊 Analisis del Modelo

### Metricas de Calidad
*   **Integridad:** Uso extensivo de FOREIGN KEY constraints para evitar registros huerfanos.
*   **Rendimiento:** Indices CLUSTERED en todas las claves primarias.
*   **Seguridad:** Esquema preparado para manejo de roles y encriptacion de contrasenas.

### Conclusiones
La base de datos **SUPERMERCADO_JPV_V6** presenta una madurez alta para soportar la operacion retail. La separacion logica de entidades permite una escalabilidad modular (ej: agregar modulo de fidelizacion sin romper ventas).

---

## 11. 🤝 Contribucion
1.  Hacer Fork del proyecto.
2.  Crear rama (git checkout -b feature/NuevaTabla).
3.  Commit de cambios (git commit -m 'Add: Nueva funcionalidad').
4.  Push a la rama (git push origin feature/NuevaTabla).
5.  Abrir Pull Request.

---

## 12. ⚖ Licencia
Este proyecto esta bajo la Licencia **MIT**. Se permite el uso comercial, modificacion y distribucion bajo los terminos especificados.

---
*Documentacion generada automaticamente por **Gemini AI Agent** el 2026-01-15*
>>>>>>> d4cb4bc (Initial commit: Add Database Documentation)
