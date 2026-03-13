# Guía de Despliegue en Red y Producción - MiniERP V10

Este documento detalla los pasos necesarios para publicar y desplegar el sistema MiniERP (Escritorio y Móvil) en un entorno de red real o en la nube.

---

### 1. Despliegue en Red Local (Recomendado para Tiendas)
Esta opción permite que todas las computadoras y celulares de la tienda se conecten a un servidor central a través del WiFi local.

#### Paso A: Preparar el Servidor Principal
La computadora que aloja la base de datos (Ej: `192.168.2.22`) será el servidor principal.
1.  **IP Estática:** Configurar una IP fija en Windows para que no cambie al reiniciar el router.
2.  **Firewall de Windows:**
    *   Abrir puerto **1433** (Entrada) para permitir conexiones a SQL Server.
    *   Abrir puerto **5000** (Entrada) para el servidor de la App Móvil.
3.  **SQL Server Configuration:**
    *   Abrir *SQL Server Configuration Manager*.
    *   Habilitar **TCP/IP** en "Protocolos de la Instancia".
    *   Reiniciar el servicio de SQL Server.

#### Paso B: Desplegar la App de Escritorio (Clientes)
1.  **Distribución:** Copiar la carpeta `dist\MiniERP_Supermercado_JPV_V9` a las otras computadoras.
2.  **Configuración:** En cada PC cliente, editar el archivo `config.json` cambiando el servidor local por la IP del servidor:
    ```json
    { "server_ip": "192.168.2.22" }
    ```

#### Paso C: Desplegar la App Móvil (mPOS)
1.  **Iniciar Servidor:** Ejecutar `MiniERP_Mobile_POS_Server.exe` en el servidor principal.
2.  **Acceso Móvil:** Los vendedores entran desde su navegador a: `http://192.168.2.22:5000`.
3.  **Instalación:** En el móvil, usar la opción "Añadir a pantalla de inicio" del navegador para crear un acceso directo con icono.

---

### 2. Despliegue en la Nube (Acceso Global)
Para acceder desde fuera de la tienda o desde otras sucursales.

#### Opción VPS (Servidor Virtual)
1.  Contratar un servidor Windows en la nube (AWS, Google Cloud, Azure).
2.  Migrar la base de datos SQL Server al servidor virtual.
3.  Ejecutar el servidor móvil en el VPS y apuntar un dominio (Ej: `pos.miempresa.com`).

#### Opción Túnel Seguro (ngrok / Cloudflare)
1.  Si no quieres contratar un servidor, puedes usar un túnel para exponer tu puerto local `5000` a internet de forma segura.

---

### 3. Matriz de Componentes

| Componente | Solución | Acción Requerida |
| :--- | :--- | :--- |
| **Base de Datos** | SQL Server Central | Habilitar TCP/IP y conexiones remotas. |
| **Desktop App** | Portable en Red | Distribuir carpeta `dist` y configurar IP en `config.json`. |
| **Mobile App** | Web App (PWA) | Mantener abierto el servidor en la PC central. |
| **Documentos** | PDF Local | Los archivos se descargan directamente en cada dispositivo. |

---
**Documento generado para Ing. Juancito Peña - 13 de Marzo, 2026**
