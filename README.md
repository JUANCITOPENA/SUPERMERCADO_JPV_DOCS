# 🛒 SUPERMERCADO_JPV_V6 - Documentacion Oficial

![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)
![Database](https://img.shields.io/badge/SQL_Server-Enterprise-red.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

> **Nota:** Esta documentacion se genera automaticamente analizando el script fuente oficial BASE DE DATOS SUPERMERCADO_JPV_V6.sql.

---

## 📂 Tabla de Contenidos
1. [Planteamiento](#planteamiento)
2. [Objetivos](#objetivos)
3. [Stack Tecnologico](#stack)
4. [Instalacion](#instalacion)
5. [Diccionario de Datos (Modelo Detallado)](#modelo)
6. [Contribucion](#contribucion)

---

## <a name="planteamiento"></a>1. 🚩 Planteamiento
El sistema **SUPERMERCADO_JPV_V6** es la solucion integral para la gestion retail. Resuelve la fragmentacion de datos unificando inventario, ventas y contabilidad en un esquema relacional robusto.

## <a name="objetivos"></a>2. 🎯 Objetivos
- **Centralizacion:** Unica fuente de verdad para N sucursales.
- **Integridad:** Reglas de negocio forzadas a nivel de base de datos (Constraints).
- **Rendimiento:** Optimizado para lecturas masivas (Reportes) y escritura transaccional (POS).

## <a name="stack"></a>3. 🛠 Tecnologias
- **Motor:** SQL Server 2019+
- **Integracion:** Entity Framework Core / Dapper
- **OS:** Windows Server / Linux

## <a name="instalacion"></a>4. ⚙ Instalacion
1. Clonar este repositorio.
2. Abrir SSMS (SQL Server Management Studio).
3. Ejecutar el script BASE DE DATOS SUPERMERCADO_JPV_V6.sql.
4. Configurar connection strings en la APP.

---

## <a name="modelo"></a>5. 🧩 Diccionario de Datos
A continuacion se describe el modelo de datos agrupado por areas funcionales, tal como se define en el script de despliegue.

### ⚙ Procedimientos y Logica
- ⚡ **SP_ACTUALIZAR_CLIENTE** (PROCEDURE)
- ⚡ **SP_CREAR_CLIENTE** (PROCEDURE)
- ⚡ **SP_FACTURAR_VENTA** (PROCEDURE)
---

## <a name="contribucion"></a>6. 🤝 Contribucion
Si deseas mejorar el modelo:
1. Modifica el script SQL.
2. Actualiza la documentacion.
3. Envia un Pull Request.

---
*Generado automaticamente por Gemini Agent.*
