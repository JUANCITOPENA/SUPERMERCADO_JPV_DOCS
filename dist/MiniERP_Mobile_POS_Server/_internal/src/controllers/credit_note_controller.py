from src.config.database import db
import datetime
import traceback

class CreditNoteController:
    def search_invoices(self, criteria=None):
        """Busca facturas que aun pueden ser afectadas por Notas de Credito."""
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
        """Obtiene el detalle de la factura calculando el SALDO DISPONIBLE por cada item."""
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

            # Detalles usando el nuevo SP que trae 'Ya_Devuelto'
            cursor.execute("EXEC SP_GET_FACTURA_DETALLE_PARA_NC @ID_Venta=?", (id_venta,))
            
            for r in cursor.fetchall():
                cant_orig = r[2]
                ya_devuelto = r[3]
                disponible = cant_orig - ya_devuelto
                
                if disponible >= 0: # Solo agregar si queda algo o si es cero pero fue facturado
                    data["items"].append({
                        "id_producto": r[0],
                        "producto": r[1],
                        "cantidad_original": cant_orig,
                        "ya_devuelto": ya_devuelto,
                        "disponible": disponible,
                        "precio": float(r[4]),
                        "itbis": float(r[5]),
                        "qty_refund": 0
                    })
            
            return data, None
        except Exception as e:
            print(traceback.format_exc())
            return None, str(e)
        finally:
            if 'conn' in locals(): conn.close()

    def create_credit_note(self, data):
        """Procesa la creacion de la Nota de Credito, actualiza stock y estado de factura."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            conn.autocommit = False

            # 1. Calcular totales de la NC
            total_dev = sum(it['qty_refund'] * it['precio'] for it in data['items'])
            itbis_dev = sum(it['qty_refund'] * it['itbis'] for it in data['items'])
            
            # Determinar si es TOTAL o PARCIAL basado en si queda algo por devolver
            # Si todas las cantidades 'qty_refund' igualan a las 'disponible', es un cierre total
            es_cierre_total = True
            for it in data['items']:
                if it['qty_refund'] < it['disponible']:
                    es_cierre_total = False
                    break
            
            tipo_nc = "TOTAL" if (data.get('es_total', False) or es_cierre_total) else "PARCIAL"

            # 2. Crear Cabecera mediante SP
            cursor.execute("""
                EXEC SP_CREAR_NOTA_CREDITO_PRO 
                @ID_Venta=?, @Usuario=?, @Motivo=?, @Tipo=?, @MontoTotal=?, @ItbisTotal=?
            """, (data['id_venta'], data['usuario'], data['motivo'], tipo_nc, total_dev, itbis_dev))
            
            res = cursor.fetchone()
            id_nc = res[0]
            ncf_nc = res[1]

            # 3. Insertar Detalles y devolver Stock
            for it in data['items']:
                if it['qty_refund'] <= 0: continue
                
                # Detalle NC
                cursor.execute("""
                    INSERT INTO DETALLE_NOTA_CREDITO (ID_NOTA, ID_PRODUCTO, CANTIDAD_DEVUELTA, PRECIO_UNITARIO_REF)
                    VALUES (?, ?, ?, ?)
                """, (id_nc, it['id_producto'], it['qty_refund'], it['precio']))

                # Update Stock en tabla PRODUCTO
                cursor.execute("UPDATE PRODUCTO SET STOCK = STOCK + ? WHERE ID_PRODUCTO = ?", (it['qty_refund'], it['id_producto']))

            conn.commit()
            return True, f"Nota de Credito {ncf_nc} generada con exito.", id_nc
        except Exception as e:
            print(traceback.format_exc())
            if 'conn' in locals(): conn.rollback()
            return False, f"Error al procesar NC: {str(e)}", None
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

    def get_nc_full_details(self, id_nota):
        """Obtiene toda la informacion de una NC para impresion profesional."""
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
            
            # Items devueltos en esta NC especifica
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
