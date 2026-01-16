from src.config.database import db
from datetime import datetime
import calendar

class DashboardController:
    def get_filters_data(self):
        """Obtiene datos para poblar los filtros de la UI."""
        data = {"years": [], "clients": []}
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            # Años disponibles
            cursor.execute("SELECT DISTINCT YEAR(FECHA) FROM VENTAS ORDER BY YEAR(FECHA) DESC")
            data["years"] = [str(row[0]) for row in cursor.fetchall()]
            
            # Clientes (ID, Nombre) - Ordenados Alfabéticamente
            cursor.execute("SELECT ID_CLIENTE, CONCAT(NOMBRE_CLIENTE, ' ', APELLIDO_CLIENTE) FROM CLIENTE ORDER BY NOMBRE_CLIENTE ASC")
            data["clients"] = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
            
            conn.close()
        except Exception as e:
            print(f"Error Filters: {e}")
        return data

    def _build_query_conditions(self, year=None, month=None, client_id=None):
        """Construye cláusulas WHERE dinámicas."""
        clauses = ["ESTADO = 'COMPLETADA'"] # Regla de oro: Solo ventas reales
        
        if year and year != "Todos":
            clauses.append(f"YEAR(FECHA) = {year}")
            
            if month and month != "Todos":
                # Convertir nombre de mes a número
                month_num = list(calendar.month_name).index(month) if month in calendar.month_name else None
                # En español simple mapping si es necesario, asumiremos index standard
                months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                if month in months_es:
                    month_num = months_es.index(month)
                
                if month_num:
                    clauses.append(f"MONTH(FECHA) = {month_num}")
        
        if client_id:
            clauses.append(f"ID_CLIENTE = {client_id}")
            
        return " AND ".join(clauses)

    def get_kpis(self, year=None, month=None, client_id=None):
        """KPIs financieros filtrados dinámicamente."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            where_sql = self._build_query_conditions(year, month, client_id)

            # 1. Ingresos
            sql = f"SELECT ISNULL(SUM(TOTAL_VENTA), 0) FROM VENTAS WHERE {where_sql}"
            cursor.execute(sql)
            total_revenue = float(cursor.fetchone()[0])

            # 2. Costos (Aproximación por costo actual)
            sql_cost = f"""
                SELECT ISNULL(SUM(d.Cantidad * p.PRECIO_COMPRA), 0)
                FROM DETALLE_VENTAS d
                JOIN PRODUCTO p ON d.ID_Producto = p.ID_Producto
                JOIN VENTAS v ON d.ID_Venta = v.ID_Venta
                WHERE {where_sql.replace('ESTADO', 'v.ESTADO').replace('YEAR(FECHA)', 'YEAR(v.FECHA)').replace('MONTH(FECHA)', 'MONTH(v.FECHA)').replace('ID_CLIENTE', 'v.ID_CLIENTE')}
            """
            cursor.execute(sql_cost)
            total_cost = float(cursor.fetchone()[0])

            # 3. Transacciones
            cursor.execute(f"SELECT COUNT(*) FROM VENTAS WHERE {where_sql}")
            trans = int(cursor.fetchone()[0])

            # 4. Unidades
            sql_units = f"""
                SELECT ISNULL(SUM(d.Cantidad), 0)
                FROM DETALLE_VENTAS d
                JOIN VENTAS v ON d.ID_Venta = v.ID_Venta
                WHERE {where_sql.replace('ESTADO', 'v.ESTADO').replace('YEAR(FECHA)', 'YEAR(v.FECHA)').replace('MONTH(FECHA)', 'MONTH(v.FECHA)').replace('ID_CLIENTE', 'v.ID_CLIENTE')}
            """
            cursor.execute(sql_units)
            units = int(cursor.fetchone()[0])

            conn.close()
            
            margin = total_revenue - total_cost
            margin_pct = (margin / total_revenue * 100) if total_revenue > 0 else 0
            ticket = (total_revenue / trans) if trans > 0 else 0

            return {
                "ingresos": total_revenue,
                "costos": total_cost,
                "margen": margin,
                "margen_pct": margin_pct,
                "transacciones": trans,
                "unidades": units,
                "ticket_promedio": ticket
            }
        except Exception as e:
            print(f"KPI Error: {e}")
            return {}

    def get_charts_data(self, year=None, month=None, client_id=None):
        """Datos para gráficos y tablas."""
        try:
            conn = db.connect()
            cursor = conn.cursor()
            where_sql = self._build_query_conditions(year, month, client_id)
            
            # Gráfico: Tendencia (Si es mes -> por días, Si es año -> por meses, Si es histórico -> por años)
            # Simplificación: Siempre por Fecha (top 15 puntos)
            sql_chart = f"""
            SELECT TOP 15 FORMAT(FECHA, 'yyyy-MM-dd') as F, SUM(TOTAL_VENTA)
            FROM VENTAS
            WHERE {where_sql}
            GROUP BY FORMAT(FECHA, 'yyyy-MM-dd'), CAST(FECHA as DATE)
            ORDER BY CAST(FECHA as DATE) ASC
            """
            cursor.execute(sql_chart)
            chart_data = cursor.fetchall()

            # Top Productos (Filtrado)
            sql_top = f"""
            SELECT TOP 10 P.PRODUCTO, SUM(D.Cantidad) as Qty, SUM(D.SUBTOTAL) as Total
            FROM DETALLE_VENTAS D
            JOIN PRODUCTO P ON D.ID_Producto = P.ID_Producto
            JOIN VENTAS V ON D.ID_Venta = V.ID_Venta
            WHERE {where_sql.replace('ESTADO', 'V.ESTADO').replace('YEAR(FECHA)', 'YEAR(V.FECHA)').replace('MONTH(FECHA)', 'MONTH(V.FECHA)').replace('ID_CLIENTE', 'V.ID_CLIENTE')}
            GROUP BY P.PRODUCTO
            ORDER BY Qty DESC
            """
            cursor.execute(sql_top)
            top_products = cursor.fetchall()

            conn.close()
            return ([r[0] for r in chart_data], [float(r[1]) for r in chart_data]), top_products

        except Exception as e:
            print(f"Chart Error: {e}")
            return ([], []), []