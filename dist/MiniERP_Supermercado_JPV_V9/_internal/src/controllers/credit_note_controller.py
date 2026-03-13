from src.config.database import db
import datetime
import traceback

class CreditNoteController:
    def search_invoices(self, criteria=None):
        """Busca facturas elegibles para aplicar notas de credito."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("EXEC SP_BUSCAR_FACTURAS_PARA_NC @Criterio=?", (criteria,))
            rows = cursor.fetchall()
            return [{"id_venta": r[0], "ncf": r[1], "cliente": r[2], "total": float(r[3]), "fecha": r[4], "estado": r[5]} for r in rows]
        except:
            print(traceback.format_exc())
            return []
        finally:
            if 'conn' in locals(): conn.close()

    def get_invoice_details(self, id_venta):
        """Obtiene el detalle de una factura especifica."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            # Encabezado
            cursor.execute("SELECT NCF_GENERADO, TOTAL_VENTA, ESTADO FROM VENTAS WHERE ID_VENTA = ?", (id_venta,))
            header = cursor.fetchone()
            if not header: return None, "Factura no encontrada"

            data = {
                "id_venta": id_venta,
                "ncf": header[0],
                "total": float(header[1]),
                "estado": header[2],
                "items": []
            }

            # Detalles
            cursor.execute("""
                SELECT d.ID_PRODUCTO, p.PRODUCTO, d.CANTIDAD, d.PRECIO_UNITARIO, d.ITBIS_UNITARIO
                FROM DETALLE_VENTAS d
                JOIN PRODUCTO p ON d.ID_PRODUCTO = p.ID_PRODUCTO
                WHERE d.ID_VENTA = ?
            """, (id_venta,))
            
            for r in cursor.fetchall():
                data["items"].append({
                    "id_producto": r[0],
                    "producto": r[1],
                    "cantidad_original": r[2],
                    "precio": float(r[3]),
                    "itbis": float(r[4]),
                    "qty_refund": 0
                })
            
            return data, None
        except Exception as e:
            return None, str(e)
        finally:
            if 'conn' in locals(): conn.close()

    def create_credit_note(self, data):
        """Procesa la creacion de la Nota de Credito y actualiza stock."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            conn.autocommit = False

            # 1. Crear Cabecera mediante SP
            total_dev = sum(it['qty_refund'] * it['precio'] for it in data['items'])
            itbis_dev = sum(it['qty_refund'] * it['itbis'] for it in data['items'])
            tipo = "TOTAL" if data.get('es_total', False) else "PARCIAL"

            cursor.execute("""
                EXEC SP_CREAR_NOTA_CREDITO_PRO 
                @ID_Venta=?, @Usuario=?, @Motivo=?, @Tipo=?, @MontoTotal=?, @ItbisTotal=?
            """, (data['id_venta'], data['usuario'], data['motivo'], tipo, total_dev, itbis_dev))
            
            res = cursor.fetchone()
            id_nc = res[0]
            ncf_nc = res[1]

            # 2. Insertar Detalles y devolver Stock
            for it in data['items']:
                if it['qty_refund'] <= 0: continue
                
                # Detalle NC
                cursor.execute("""
                    INSERT INTO DETALLE_NOTA_CREDITO (ID_NOTA, ID_PRODUCTO, CANTIDAD_DEVUELTA, PRECIO_UNITARIO_REF)
                    VALUES (?, ?, ?, ?)
                """, (id_nc, it['id_producto'], it['qty_refund'], it['precio']))

                # Update Stock
                cursor.execute("UPDATE PRODUCTO SET STOCK = STOCK + ? WHERE ID_PRODUCTO = ?", (it['qty_refund'], it['id_producto']))

            conn.commit()
            return True, f"Nota de Credito {ncf_nc} generada con exito.", id_nc
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            return False, f"Error al procesar: {str(e)}", None
        finally:
            if 'conn' in locals(): conn.close()

    def get_nc_full_details(self, id_nota):
        """Obtiene toda la informacion de una NC para impresion."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            # Cabecera
            cursor.execute("""
                SELECT N.NCF_NOTA_CREDITO, N.NCF_FACTURA_ORIGINAL, N.FECHA, N.MOTIVO, N.TOTAL_DEVUELTO,
                       CONCAT(C.NOMBRE_CLIENTE, ' ', C.APELLIDO_CLIENTE), C.RNC_CEDULA
                FROM NOTA_CREDITO N
                JOIN VENTAS V ON N.ID_VENTA = V.ID_VENTA
                JOIN CLIENTE C ON V.ID_CLIENTE = C.ID_CLIENTE
                WHERE N.ID_NOTA = ?
            """, (id_nota,))
            r = cursor.fetchone()
            if not r: return None, None
            
            nc_info = {
                "ncf": r[0], "ncf_ref": r[1], "fecha": r[2], "motivo": r[3],
                "total": float(r[4]), "cliente": r[5], "rnc": r[6]
            }
            
            # Items
            cursor.execute("""
                SELECT P.PRODUCTO, D.CANTIDAD_DEVUELTA, D.PRECIO_UNITARIO_REF
                FROM DETALLE_NOTA_CREDITO D
                JOIN PRODUCTO P ON D.ID_PRODUCTO = P.ID_PRODUCTO
                WHERE D.ID_NOTA = ?
            """, (id_nota,))
            
            items = [{"name": row[0], "qty": row[1], "price": float(row[2]), "total": row[1]*float(row[2])} for row in cursor.fetchall()]
            
            return nc_info, items
        except:
            return None, None
        finally:
            if 'conn' in locals(): conn.close()

    def list_credit_notes(self, criteria=None, start_date=None, end_date=None):
        """Lista las Notas de Credito existentes."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("EXEC SP_LISTAR_NOTAS_CREDITO_AVANZADO @Criterio=?, @FechaInicio=?, @FechaFin=?", 
                           (criteria, start_date, end_date))
            rows = cursor.fetchall()
            return [{"id": r[0], "ncf": r[1], "ref": r[2], "cliente": r[3], "fecha": r[4], "motivo": r[5], "total": float(r[6]), "id_venta": r[7]} for r in rows]
        except:
            return []
        finally:
            if 'conn' in locals(): conn.close()
