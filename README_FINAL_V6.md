# MINI ERP SUPERMERCADO JPV V6 - Python Edition 🚀

Este proyecto es una refactorización y mejora completa del sistema de gestión para el **Supermercado JPV**, implementado en **Python 3.13** utilizando tecnologías modernas de escritorio.

## 📋 Tecnologías Utilizadas
- **Lenguaje:** Python 3.13
- **Interfaz Gráfica:** CustomTkinter (Modo Claro/Moderno)
- **Base de Datos:** SQL Server 2019/2022 (Conexión ODBC 17)
- **Reportes:** ReportLab (Generación de PDFs con Imágenes)
- **Exportación de Datos:** Pandas & OpenPyXL (Excel Nativo)
- **Imágenes:** Pillow (PIL) con carga asíncrona (Thread-Safe)

## 🛠️ Módulos Implementados

### 1. 🔐 Seguridad y Acceso
- Login con validación contra base de datos.
- Hashing de contraseñas (`SHA256`).
- Gestión de Usuarios con Roles (Admin, Supervisor, Vendedor).

### 2. 🛒 Punto de Venta (POS)
- Selección inteligente de Clientes (Búsqueda por RNC/Nombre).
- **Detección automática de NCF:** Asigna comprobante Fiscal (B01) o Consumo (B02) según el tipo de cliente.
- Carga dinámica de **Vendedores**.
- Validación de **Stock en Tiempo Real**.
- Cálculo automático de ITBIS y Totales.
- **Impresión de Ticket/Factura:** Incluye desglose de impuestos, tipo de NCF y condición de pago.

### 3. 📦 Gestión de Inventario y Maestros
- **Productos:** CRUD completo con imágenes, precios de compra/venta y stock.
- **Vendedores:** Gestión de personal con foto y asignación de sucursal.
- **Clientes:** Directorio de clientes con validación de crédito.

### 4. 📊 Reportes Avanzados e Inteligencia de Negocios
- **Perfiles Individuales (PDF):** Fichas técnicas de productos y vendedores con **Foto en Grande**.
- **Catálogos Visuales (PDF):** Listados con miniaturas de imágenes.
- **Historial de Ventas:** Grid interactivo con filtros por fecha y cliente. Opción de **Reimprimir** (con marca de agua "COPIA") y **Anular Venta** (Retorno de Stock).
- **KPIs Financieros:**
    - Valoración de Inventario (Costo vs Venta).
    - Análisis de Rentabilidad por Producto (Margen %).
    - Desempeño de Vendedores (Ganancia Generada).

## 🚀 Instrucciones de Ejecución

1.  **Requisitos Previos:**
    *   Python 3.13 instalado.
    *   SQL Server con la base de datos `SUPERMERCADO_JPV_V6` restaurada.
    *   Driver ODBC 17 for SQL Server.

2.  **Instalar Dependencias:**
    ```bash
    pip install customtkinter pillow pyodbc reportlab pandas openpyxl requests
    ```

3.  **Ejecutar la Aplicación:**
    ```bash
    python main.py
    ```

4.  **Credenciales de Acceso:**
    *   **Usuario:** `Juancito`
    *   **Contraseña:** `123456`

## 📁 Estructura del Proyecto
```
MINI_ERP_SUPERMERCADO_JPV_V6_PYTHON/
├── controllers/       # Lógica de Negocio y Acceso a Datos (SQL)
├── views_ctk/         # Interfaz Gráfica (Ventanas y Formularios)
├── utils/             # Motores de Impresión, Carga de Imágenes
├── main.py            # Punto de Entrada
├── database.py        # Conexión Singleton a SQL Server
└── README_FINAL_V6.md # Este archivo
```

## ✅ Estado Final
El proyecto se encuentra **ESTABLE** y funcional. Se han corregido problemas críticos de concurrencia en la carga de imágenes y errores de sintaxis en los reportes. La conexión a la base de datos remota (10.0.0.15) está verificada.
