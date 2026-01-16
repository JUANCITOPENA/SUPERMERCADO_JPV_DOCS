# MINI ERP SUPERMERCADO JPV - V7 (PYTHON EDITION)

## 📋 Estado del Proyecto
**Estado:** Completado 🚀
**Versión:** V7.1 (Dashboard Ejecutivo + Refactor)
**Fecha:** 16 de Enero 2026

## 🌟 Características Destacadas
*   **Arquitectura Profesional:** Código reestructurado en patrón MVC (`src/controllers`, `src/views`).
*   **Dashboard Ejecutivo:**
    *   **KPIs en Tiempo Real:** Ingresos, Costos, Margen, Transacciones y Ticket Promedio.
    *   **Filtros Dinámicos:** Análisis por Año, Mes y Cliente específico.
    *   **Visualización:** Gráficos de tendencia (Matplotlib) y tablas de Top Productos estilizadas.
*   **Configuración de Red Dinámica:**
    *   Módulo de configuración para cambiar la IP del servidor (SQL Server) sin tocar el código.
    *   Persistencia en `config.json`.
    *   Acceso desde la pantalla de Login.
*   **UX Mejorada:** Centrado automático de ventanas y navegación intuitiva.
*   **Compatibilidad:** Eliminación de dependencias obsoletas (PyQt) en favor de nativas (CustomTkinter + Pillow).

## 📂 Estructura del Proyecto

```text
MINI_ERP_SUPERMERCADO_JPV_V6_PYTHON/
├── main.py                  # Lanzador Principal
├── requirements.txt         # Dependencias (ctk, pillow, matplotlib, pyodbc)
├── src/                     # Código Fuente
│   ├── config/              # Conexión DB
│   ├── controllers/         # Lógica de Negocio (Dashboard, Ventas, etc.)
│   ├── views/               # Interfaz Gráfica (Dashboard, POS, etc.)
│   └── utils/               # Motores de Reportes y Utilidades
└── scripts/                 # Scripts de Mantenimiento SQL
```

## 🛠️ Tecnologías
*   **Python 3.13**
*   **CustomTkinter** (UI Moderna)
*   **SQL Server** (Base de Datos Relacional)
*   **Matplotlib** (Analítica de Datos)
*   **ReportLab** (Generación de PDFs)

##  ▶️ Cómo Ejecutar
```powershell
python main.py
```

## 📦 Instalación
```powershell
pip install -r requirements.txt
```