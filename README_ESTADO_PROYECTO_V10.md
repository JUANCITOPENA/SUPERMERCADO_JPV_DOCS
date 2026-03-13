# MiniERP Supermercado JPV V9 - Estado del Proyecto (13 de Marzo, 2026)

Este documento detalla los avances, correcciones y el estado técnico actual del sistema tras la implementación del **Módulo de Gestión Avanzada V6**.

## 🚀 Resumen de Actualizaciones Recientes

### 1. Módulo Pro de Notas de Crédito (NCF Serie E)
Se ha implementado un sistema profesional para la gestión de devoluciones y anulaciones que cumple con los estándares fiscales:
- **Buscador Maestro:** Permite localizar facturas por ID de Cliente, Nombre, NCF o ID de Factura.
- **Tipos de Operación:**
    - **Anulación Total:** Automatiza la devolución de todos los artículos al stock y marca la factura como ANULADA.
    - **Devolución Parcial:** Permite editar cantidades mediante doble clic en el grid, calculando totales e ITBIS en tiempo real.
- **Impresión Profesional:** Generación automática de PDFs (Formato 8.5x11) con diseño corporativo para cada Nota de Crédito generada.
- **Reimpresión:** El historial permite reimprimir cualquier comprobante con solo hacer doble clic en el listado.

### 2. Interfaz de Usuario (UI/UX)
- **Calendarios Interactivos:** Integración de `tkcalendar` (DateEntry) para la selección precisa de rangos de fechas (Desde/Hasta) en los filtros.
- **Grids Dinámicos:** Los listados ahora se refrescan automáticamente y manejan grandes volúmenes de datos con scroll y ordenamiento.
- **Limpieza Visual:** Se eliminaron caracteres especiales y acentos corruptos (Ã³, Ã­) tanto en el código como en la base de datos para una lectura impecable.

### 3. Inteligencia de Negocios (BI) & Analytics
Se añadió un motor de consultas avanzadas (`BI_INSIGHTS_Y_RANKINGS_V6.sql`) que permite ver:
- **Rentabilidad Real:** Ranking de productos y vendedores basado en el margen neto (Venta - Costo).
- **Tablas Pivote:** Ventas mensuales por año, rendimiento anual de vendedores y rotación de productos por periodos.
- **KPIs de Eficiencia:** Tasa de retorno de productos y detección de "vendedores fantasma" o "productos muertos".

## 🛠️ Estado Técnico y Estructura

- **Tecnología:** Python 3.13 + CustomTkinter + SQL Server.
- **Base de Datos:** `SUPERMERCADO_JPV_V6` (Sincronizada en Local y 10.0.0.15).
- **Dependencia Nueva:** `tkcalendar` (Añadida al proceso de empaquetado).
- **Ejecutable:** Ubicado en `dist/MiniERP_Supermercado_JPV_V9/`.

## 📦 Inventario de Scripts SQL en la Raíz
1. `BASE DE DATOS SUPERMERCADO_JPV_V6.sql`: Estructura principal y carga masiva (2,000 ventas).
2. `MODULO_GESTION_AVANZADA_V6.sql`: Tablas de Logística, Notas de Crédito y Caja.
3. `POBLAR_GESTION_LOGISTICA_V6.sql`: Generador inteligente de data histórica de entregas y devoluciones.
4. `BI_INSIGHTS_Y_RANKINGS_V6.sql`: Motor de análisis y rankings.
5. `PRUEBAS_Y_CONSULTAS_V6.sql`: Suite de validación técnica.

## ✅ Pruebas Realizadas
- **Unit Tests:** `tests/test_credit_notes.py` ejecutado con éxito (OK).
- **Integración:** Verificación de transaccionalidad (Venta -> NC -> Stock) confirmada.
- **Despliegue:** Build de PyInstaller verificado con inclusión de recursos `tkcalendar`.

---
**Desarrollado por Gemini CLI para Ing. Juancito Peña**
