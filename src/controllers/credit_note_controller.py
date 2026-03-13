from src.config.database import db
import datetime
import traceback

class CreditNoteController:
    def get_invoice_details(self, ncf):
        """Busca una factura usando SQL directo para evitar fallos de SP."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            ncf_input = str(ncf).strip()
            if not ncf_input:
                return None, "El NCF está vacío."

            # 1. Buscar el encabezado de la venta (Búsqueda flexible)
            sql_header = """
                SELECT ID_VENTA, NCF_GENERADO, TOTAL_VENTA, FECHA, ESTADO 
                FROM VENTAS 
                WHERE LTRIM(RTRIM(NCF_GENERADO)) = ? 
                OR NCF_GENERADO LIKE ?
            """
            cursor.execute(sql_header, (ncf_input, f"%{ncf_input}%"))
            header = cursor.fetchone()
            
            if not header:
                # Si falla, intentar buscar una lista de sugerencias para ayudar al usuario
                cursor.execute("SELECT TOP 3 NCF_GENERADO FROM VENTAS ORDER BY FECHA DESC")
                sug = [r[0] for r in cursor.fetchall()]
                return None, f"Factura '{ncf_input}' no encontrada.\nSugerencias recientes: {', '.join(sug)}"
            
            id_venta = header[0]
            invoice_data = {
                "id_venta": id_venta,
                "ncf": header[1],
                "total": float(header[2]),
                "fecha": header[3],
                "estado": header[4],
                "items": []
            }

            # 2. Buscar los detalles (SQL Directo)
            sql_details = """
                SELECT d.ID_PRODUCTO, p.PRODUCTO, d.CANTIDAD, d.PRECIO_UNITARIO, d.SUBTOTAL 
                FROM DETALLE_VENTAS d
                JOIN PRODUCTO p ON d.ID_PRODUCTO = p.ID_PRODUCTO
                WHERE d.ID_VENTA = ?
            """
            cursor.execute(sql_details, (id_venta,))
            rows = cursor.fetchall()
            
            for r in rows:
                invoice_data["items"].append({
                    "id_producto": r[0],
                    "producto": r[1],
                    "cantidad_original": r[2],
                    "precio": float(r[3]),
                    "subtotal": float(r[4]),
                    "qty_refund": 0
                })
            
            if not invoice_data["items"]:
                return None, "La factura existe pero no tiene artículos en su detalle."

            return invoice_data, None

        except Exception as e:
            print(f"DEBUG ERROR: {traceback.format_exc()}")
            return None, f"Error de conexión: {str(e)}"
        finally:
            if 'conn' in locals(): conn.close()

    def create_credit_note(self, data):
        """Crea la Nota de Crédito con validación estricta de montos."""
        conn = db.connect()
        try:
            cursor = conn.cursor()
            conn.autocommit = False 

            # 1. Obtener Siguiente NCF B04
            cursor.execute("SELECT ISNULL(MAX(Ultimo_Numero), 0) + 1 FROM SECUENCIAS_NCF WHERE Tipo = 'B04'")
            next_num = int(cursor.fetchone()[0])
            ncf_nc = f"B04{str(next_num).zfill(8)}"
            
            # 2. Calcular e Insertar Encabezado
            total_nc = sum([i['cantidad'] * i['precio'] for i in data['items']])
            
            # Usamos OUTPUT para asegurar el ID
            sql_ins_nc = """
                INSERT INTO NOTAS_CREDITO (NCF_Nota, NCF_Afectado, Tipo, Monto_Total, Usuario_Creador, Comentario)
                OUTPUT INSERTED.ID_Nota
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql_ins_nc, (ncf_nc, data['ncf_afectado'], data['tipo'], total_nc, data['usuario'], data['comentario']))
            id_nc = int(cursor.fetchone()[0])

            # 3. Insertar Detalles y devolver STOCK
            for item in data['items']:
                # Detalle NC
                cursor.execute("""
                    INSERT INTO DETALLE_NOTA_CREDITO (ID_Nota, ID_Producto, Cantidad, Precio_Unitario, Subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_nc, item['id_producto'], item['cantidad'], item['precio'], (item['cantidad']*item['precio'])))

                # Devolución a Almacén
                cursor.execute("UPDATE PRODUCTO SET STOCK = STOCK + ? WHERE ID_PRODUCTO = ?", (item['cantidad'], item['id_producto']))

            # 4. Actualizar Estado de la Factura Original (NCF_GENERADO)
            cursor.execute("SELECT TOTAL_VENTA FROM VENTAS WHERE NCF_GENERADO = ?", (data['ncf_afectado'],))
            row_v = cursor.fetchone()
            total_orig = float(row_v[0]) if row_v else 0
            
            nuevo_estado = "ANULADA" if total_nc >= total_orig else "NC_PARCIAL"
            cursor.execute("UPDATE VENTAS SET ESTADO = ? WHERE NCF_GENERADO = ?", (nuevo_estado, data['ncf_afectado']))

            # 5. Actualizar Secuencia
            cursor.execute("IF EXISTS (SELECT 1 FROM SECUENCIAS_NCF WHERE Tipo = 'B04') UPDATE SECUENCIAS_NCF SET Ultimo_Numero = ? WHERE Tipo = 'B04' ELSE INSERT INTO SECUENCIAS_NCF VALUES ('B04', ?)", (next_num, next_num))

            conn.commit()
            return True, f"Nota de Crédito {ncf_nc} generada. Factura {data['ncf_afectado']} marcada como {nuevo_estado}."

        except Exception as e:
            conn.rollback()
            return False, f"Error al procesar: {str(e)}"
        finally:
            conn.close()

    def get_recent_invoices(self):
        """Lista rápida de facturas elegibles."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 30 V.NCF_GENERADO, C.NOMBRE_CLIENTE, V.TOTAL_VENTA, V.ESTADO
                FROM VENTAS V JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
                WHERE V.ESTADO IN ('COMPLETADA', 'NC_PARCIAL')
                ORDER BY V.FECHA DESC
            """)
            return [{"ncf": r[0], "cliente": r[1], "total": float(r[2]), "estado": r[3]} for r in cursor.fetchall()]
        except: return []
        finally:
            if 'conn' in locals(): conn.close()
