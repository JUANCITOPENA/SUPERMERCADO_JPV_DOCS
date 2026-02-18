# Guía de Compilación y Empaquetado - Mini ERP Supermercado JPV V6

Este documento describe cómo generar el ejecutable para Windows x64.

## Especificaciones de Empaquetado
- **Plataforma:** Windows (10/11)
- **Arquitectura:** x64
- **Formato:** Carpeta Independiente (Portable)
- **Dependencias:** Python 3.x, CustomTkinter, PyInstaller
- **Config. Entorno:** Incluye `config.json` para la IP del servidor SQL Server.

## Pasos para Compilar
1. Abrir la terminal de VS Code o PowerShell.
2. Navegar al directorio raíz del proyecto.
3. Ejecutar el script automatizado:
   ```bash
   python build_exe_v6.py
   ```
4. Al finalizar, el ejecutable estará en la carpeta `dist/MiniERP_Supermercado_JPV_V6`.

## Estructura del Resultado
- `dist/MiniERP_Supermercado_JPV_V6/MiniERP_Supermercado_JPV_V6.exe`: Aplicación principal.
- `dist/MiniERP_Supermercado_JPV_V6/config.json`: Archivo editable para cambiar la IP del servidor.
- `dist/MiniERP_Supermercado_JPV_V6/imagenes_proyecto`: Recursos visuales del programa.
- `dist/MiniERP_Supermercado_JPV_V6/docs`: Documentación del sistema.

## Notas Técnicas
- El script usa `PyInstaller` con el flag `--onedir` para mayor estabilidad con recursos externos.
- Se ha incluido el comando `--collect-all customtkinter` para asegurar que el tema visual se cargue correctamente en el ejecutable.
- No se requiere instalar Python en la máquina destino para ejecutar el programa resultante.
