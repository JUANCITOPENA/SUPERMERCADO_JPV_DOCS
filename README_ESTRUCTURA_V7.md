# MINI ERP SUPERMERCADO JPV - V7 REFACTOR (PYTHON)

## 📋 Estado del Proyecto
**Estado:** Estable / Reestructurado
**Fecha:** 16 de Enero 2026
**Versión:** V7.0 (Refactorización Arquitectónica)

## 🚀 Cambios Recientes y Soluciones
Se ha realizado una reingeniería completa de la estructura de carpetas para cumplir con estándares profesionales de desarrollo en Python.

### Problemas Resueltos
1.  **Error de Ruta (`main.py` no encontrado):** Al mover el código fuente a `src/`, el comando habitual fallaba.
    *   *Solución:* Se creó un archivo `main.py` en la raíz que actúa como "wrapper" o lanzador, redirigiendo correctamente a `src.main`.
2.  **Conflicto de Librerías Gráficas:** El proyecto mezclaba `PyQt6` y `CustomTkinter`, causando inestabilidad y errores en la carga de imágenes.
    *   *Solución:* Se eliminó `PyQt6` y se reescribió la lógica de imágenes en `src/utils` usando `Pillow` (PIL), nativo y compatible con CustomTkinter.
3.  **Importaciones Rotas:** Las referencias a módulos fallaban tras el movimiento de archivos.
    *   *Solución:* Se estandarizaron todas las importaciones usando rutas absolutas desde `src` (ej. `from src.views import...`).

## 📂 Nueva Arquitectura de Carpetas

```text
MINI_ERP_SUPERMERCADO_JPV_V6_PYTHON/
├── main.py                  # <--- EJECUTAR ESTE ARCHIVO (Punto de entrada)
├── run.py                   # Lanzador alternativo
├── requirements.txt         # Dependencias limpias (sin PyQt)
├── src/                     # CÓDIGO FUENTE PRINCIPAL
│   ├── main.py              # Lógica de arranque interna
│   ├── config/              # Configuración (Database, constantes)
│   ├── controllers/         # Lógica de Negocio
│   ├── views/               # Interfaz Gráfica (CustomTkinter)
│   ├── utils/               # Utilidades (Imágenes, PDF, Excel)
│   └── assets/              # Recursos estáticos
├── scripts/                 # Scripts de mantenimiento y parches DB
├── tests/                   # Tests de integración
└── docs/                    # Documentación
```

## 🛠️ Tecnologías y Entorno
*   **Lenguaje:** Python 3.13
*   **GUI:** CustomTkinter (Modo Light/Dark)
*   **Base de Datos:** SQL Server (IP: `10.0.0.15` / Auth: `JUANCITO/123456`)
*   **Reportes:** ReportLab (PDF), XlsxWriter (Excel)
*   **Imágenes:** Pillow (PIL)

##  ▶️ Cómo Ejecutar
Simplemente corre el siguiente comando en la raíz del proyecto:

```powershell
python main.py
```

## 📦 Instalación de Dependencias
Si mueves el proyecto a otro equipo, instala las librerías necesarias:

```powershell
pip install -r requirements.txt
```
