
# MINI ERP SUPERMERCADO JPV V6 - Python Edition

Este proyecto ha sido actualizado y completado siguiendo los requerimientos de la V6.

## Tecnologías
- **Lenguaje**: Python 3.13
- **GUI**: CustomTkinter (Light Mode Moderno)
- **Base de Datos**: SQL Server (LocalDB)
- **Reportes**: ReportLab (PDF)
- **Imágenes**: Pillow (Carga asíncrona)

## Módulos Implementados
1.  **Autenticación**: Login seguro con Hash SHA256 (BD).
2.  **Dashboard**: Sidebar de navegación y área de contenido dinámica.
3.  **POS (Punto de Venta)**:
    - Búsqueda de Clientes (RNC/Nombre).
    - Detección automática de NCF (B01/B02) según tipo de cliente.
    - Búsqueda de Productos con validación de Stock.
    - Carrito de Compras con cálculo de ITBIS y Subtotal.
    - Facturación e Impresión de PDF.
4.  **Clientes**: CRUD completo con validación de RNC y Geografía.
5.  **Productos**: CRUD con gestión de Stock, Precios e Imágenes.
6.  **Vendedores**: CRUD con asignación de Sucursal y Foto.

## Ejecución
Ejecutar el archivo principal:
```bash
python main.py
```

## Estructura
- `views_ctk/`: Interfaz Gráfica (Ventanas).
- `controllers/`: Lógica de Negocio y SQL.
- `utils/`: Motores de impresión y carga de imágenes.
- `database.py`: Conexión Singleton a SQL Server.

## Notas
- Se ha mantenido la compatibilidad con la base de datos `SUPERMERCADO_JPV_V6`.
- El SP original `SP_FACTURAR_VENTA` fue reemplazado por una lógica transaccional en Python (`SalesController.process_full_sale`) para soportar múltiples items por factura correctamente.
