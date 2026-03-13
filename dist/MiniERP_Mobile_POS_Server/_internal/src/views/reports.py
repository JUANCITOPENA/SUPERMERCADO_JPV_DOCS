import customtkinter as ctk
from tkinter import messagebox
from src.views.styles import Colors, Fonts
from src.controllers.report_controller import ReportController
from src.controllers.client_controller import ClientController
from src.controllers.vendor_controller import VendorController
from src.controllers.products_controller import ProductController
from src.utils.print_engine import PrintEngine
from datetime import datetime
from tkcalendar import DateEntry

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = ReportController()
        self.cli_ctrl = ClientController()
        self.ven_ctrl = VendorController()
        self.prod_ctrl = ProductController()
        
        self.create_ui()

    def create_ui(self):
        # Header
        ctk.CTkLabel(self, text="📊 Centro de Reportes Avanzados", font=Fonts.TITLE).pack(pady=20)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_clients = self.tabview.add("👥 Clientes")
        self.tab_vendors = self.tabview.add("👔 Vendedores")
        self.tab_products = self.tabview.add("📦 Productos")
        self.tab_nc = self.tabview.add("📝 Notas de Crédito")
        self.tab_inventory = self.tabview.add("📋 Inventario")
        
        self.build_clients_tab()
        self.build_vendors_tab()
        self.build_products_tab()
        self.build_nc_tab()
        self.build_inventory_tab()

    def _create_card(self, parent, title, row, col):
        card = ctk.CTkFrame(parent, fg_color=Colors.PANEL, corner_radius=10)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(card, text=title, font=Fonts.SUBTITLE, text_color=Colors.PRIMARY).pack(pady=10)
        return card

    def build_clients_tab(self):
        frm = self.tab_clients
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        
        # --- Reporte Individual Pro ---
        card_ind = self._create_card(frm, "📄 Reporte Individual de Cliente", 0, 0)
        
        # Combo Cliente
        self.clients = self.cli_ctrl.get_all()
        vals = [f"{c[0]} - {c[1]} {c[2]}" for c in self.clients]
        self.cmb_cli = ctk.CTkComboBox(card_ind, values=vals, width=300)
        self.cmb_cli.pack(pady=10)
        
        # Filtros de Fecha (Picker)
        date_frm = ctk.CTkFrame(card_ind, fg_color="transparent")
        date_frm.pack(pady=10)
        
        ctk.CTkLabel(date_frm, text="Desde:").grid(row=0, column=0, padx=5)
        self.cli_since = DateEntry(date_frm, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.cli_since.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(date_frm, text="Hasta:").grid(row=0, column=2, padx=5)
        self.cli_until = DateEntry(date_frm, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.cli_until.grid(row=0, column=3, padx=5)
        
        # Botones
        ctk.CTkButton(card_ind, text="🚀 Generar Reporte Completo (PDF)", command=self.gen_client_comprehensive_pdf, 
                     fg_color=Colors.DANGER, height=40, font=Fonts.BUTTON).pack(pady=15)
        
        ctk.CTkButton(card_ind, text="Ver Resumen en Pantalla", command=self.load_client_stats, fg_color="gray").pack(pady=5)
        self.lbl_cli_stats = ctk.CTkLabel(card_ind, text="Seleccione cliente para ver acumulados.")
        self.lbl_cli_stats.pack(pady=10)

        # --- Listado General ---
        card_gen = self._create_card(frm, "📑 Exportaciones Maestras", 0, 1)
        ctk.CTkLabel(card_gen, text="Genera un archivo Excel con toda la base de datos\nde clientes, incluyendo creditos y contactos.").pack(pady=20)
        ctk.CTkButton(card_gen, text="📥 Exportar Clientes a Excel", command=self.export_client_list, fg_color=Colors.SUCCESS, height=40).pack(pady=10)

    def gen_client_comprehensive_pdf(self):
        try:
            val = self.cmb_cli.get()
            if not val: return
            cid = int(val.split(" - ")[0])
            
            since = self.cli_since.get_date().strftime('%Y-%m-%d')
            until = self.cli_until.get_date().strftime('%Y-%m-%d')
            
            # 1. Obtener Info Maestra
            c_data = next((c for c in self.clients if c[0] == cid), None)
            info = {
                "ID Cliente": cid,
                "Nombre Completo": f"{c_data[1]} {c_data[2]}",
                "RNC / Cedula": c_data[3],
                "Tipo de Persona": c_data[4],
                "Direccion": c_data[5],
                "Provincia": c_data[9],
                "Periodo Reporte": f"Del {since} al {until}"
            }
            
            # 2. Obtener Estadisticas
            stats_raw = self.controller.get_client_stats(cid)
            stats = {
                "Total Facturado (Bruto)": f"RD$ {stats_raw['venta']:,.2f}",
                "Margen de Ganancia": f"RD$ {stats_raw['margen_moneda']:,.2f}",
                "Rentabilidad (%)": f"{stats_raw['margen_porc']:.1f}%",
                "Frecuencia de Compra": f"{stats_raw['compras']} facturas"
            }
            
            # 3. Obtener Transacciones (Ventas + NC) filtradas
            txns = self.controller.get_client_transactions_report(cid, since, until)
            
            if not txns:
                if not messagebox.askyesno("Sin Datos", "No hay movimientos en el rango seleccionado. ¿Generar solo cabecera?"):
                    return

            filename = f"Reporte_Individual_{cid}_{datetime.now().strftime('%Y%m%d')}.pdf"
            ok, msg = PrintEngine.generate_client_comprehensive_report(
                f"Reporte Integral de Cliente: {c_data[1]}", 
                info, 
                stats, 
                txns, 
                filename
            )
            
            if ok: messagebox.showinfo("Exito", msg)
            else: messagebox.showerror("Error", msg)
            
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", str(e))

    def load_client_stats(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        stats = self.controller.get_client_stats(cid)
        txt = (f"Compras: {stats['compras']} | Total: ${stats['venta']:,.2f}\n"
               f"Margen: ${stats['margen_moneda']:,.2f} ({stats['margen_porc']:.1f}%)")
        self.lbl_cli_stats.configure(text=txt)

    def build_nc_tab(self):
        frm = self.tab_nc
        frm.grid_columnconfigure(0, weight=1)
        
        card = self._create_card(frm, "📋 Reportes Maestros de Notas de Crédito (E34)", 0, 0)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Filtros Avanzados
        filter_box = ctk.CTkFrame(card, fg_color="transparent")
        filter_box.pack(pady=10, fill="x")
        
        # Row 1: Search & Type
        row1 = ctk.CTkFrame(filter_box, fg_color="transparent")
        row1.pack(pady=5)
        
        ctk.CTkLabel(row1, text="Buscador (NCF/Cliente):", font=Fonts.BODY).pack(side="left", padx=5)
        self.nc_search = ctk.CTkEntry(row1, width=250, placeholder_text="Escriba aqui...")
        self.nc_search.pack(side="left", padx=10)
        
        ctk.CTkLabel(row1, text="Tipo de NC:", font=Fonts.BODY).pack(side="left", padx=5)
        self.nc_type_filter = ctk.CTkComboBox(row1, values=["TODAS", "TOTAL", "PARCIAL"], width=150)
        self.nc_type_filter.pack(side="left", padx=10)

        # Row 2: Dates
        row2 = ctk.CTkFrame(filter_box, fg_color="transparent")
        row2.pack(pady=5)
        
        ctk.CTkLabel(row2, text="Desde:", font=Fonts.BODY).pack(side="left", padx=5)
        self.nc_since = DateEntry(row2, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.nc_since.pack(side="left", padx=10)
        
        ctk.CTkLabel(row2, text="Hasta:", font=Fonts.BODY).pack(side="left", padx=5)
        self.nc_until = DateEntry(row2, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.nc_until.pack(side="left", padx=10)

        # Botones de Generacion
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=30)
        
        ctk.CTkButton(btn_box, text="📄 GENERAR PDF DETALLADO", command=self.gen_nc_pdf_report, 
                     fg_color=Colors.DANGER, width=220, height=45, font=Fonts.BUTTON).pack(side="left", padx=20)
        
        ctk.CTkButton(btn_box, text="Excel EXPORTAR MAESTRO NC", command=self.export_nc_excel, 
                     fg_color=Colors.SUCCESS, width=220, height=45, font=Fonts.BUTTON).pack(side="left", padx=20)

    def gen_nc_pdf_report(self):
        try:
            criteria = self.nc_search.get()
            since = self.nc_since.get_date().strftime('%Y-%m-%d')
            until = self.nc_until.get_date().strftime('%Y-%m-%d')
            type_f = self.nc_type_filter.get()
            
            data = self.controller.get_credit_notes_report_data(criteria, since, until)
            if type_f != "TODAS":
                data = [r for r in data if r[6] == type_f]
                
            summary = self.controller.get_credit_notes_summary(since, until)
            
            cols = ["ID", "NCF Nota", "Factura Ref", "Cliente", "Fecha", "Motivo", "Tipo", "Total Dev", "ITBIS"]
            date_narrative = f"Periodo Filtrado: {since} al {until} | Tipo: {type_f}"
            
            ok, msg = PrintEngine.generate_credit_notes_general_report("Reporte General de Notas de Crédito", data, cols, summary, date_narrative)
            if ok: messagebox.showinfo("Éxito", msg)
            else: messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_nc_excel(self):
        try:
            criteria = self.nc_search.get()
            since = self.nc_since.get_date().strftime('%Y-%m-%d')
            until = self.nc_until.get_date().strftime('%Y-%m-%d')
            type_f = self.nc_type_filter.get()
            
            data = self.controller.get_credit_notes_report_data(criteria, since, until)
            if type_f != "TODAS":
                data = [r for r in data if r[6] == type_f]
                
            headers = ["ID NC", "NCF E34", "NCF Original", "Cliente", "Fecha Emision", "Motivo", "Tipo", "Total Devuelto", "ITBIS Devuelto"]
            
            filename = f"Maestro_Notas_Credito_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            ok, msg = self.controller.export_to_excel(data, headers, filename)
            if ok: messagebox.showinfo("Excel Generado", msg)
            else: messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- OTHER TABS ---
    def build_vendors_tab(self):
        frm = self.tab_vendors
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        
        # --- Ficha Detallada Pro ---
        card_ind = self._create_card(frm, "📄 Ficha de Vendedor Detallada", 0, 0)
        
        self.vendors = self.ven_ctrl.get_all() 
        vals = [f"{v[0]} - {v[1]}" for v in self.vendors]
        self.cmb_ven = ctk.CTkComboBox(card_ind, values=vals, width=250)
        self.cmb_ven.pack(pady=10)
        
        # Filtros de Fecha
        date_frm = ctk.CTkFrame(card_ind, fg_color="transparent")
        date_frm.pack(pady=10)
        
        ctk.CTkLabel(date_frm, text="Desde:").grid(row=0, column=0, padx=5)
        self.ven_since = DateEntry(date_frm, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.ven_since.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(date_frm, text="Hasta:").grid(row=0, column=2, padx=5)
        self.ven_until = DateEntry(date_frm, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.ven_until.grid(row=0, column=3, padx=5)
        
        ctk.CTkButton(card_ind, text="🚀 Generar Ficha Integral (PDF)", command=self.gen_vendor_comprehensive_pdf, 
                     fg_color=Colors.PRIMARY, height=40, font=Fonts.BUTTON).pack(pady=15)
        
        # --- Catalogo General ---
        card_cat = self._create_card(frm, "📚 Reportes de Gestion", 0, 1)
        ctk.CTkButton(card_cat, text="Generar Catalogo de Vendedores (PDF)", command=self.gen_vendor_catalog, height=40).pack(pady=10)

    def gen_vendor_comprehensive_pdf(self):
        try:
            val = self.cmb_ven.get()
            if not val: return
            vid = int(val.split(" - ")[0])
            
            since = self.ven_since.get_date().strftime('%Y-%m-%d')
            until = self.ven_until.get_date().strftime('%Y-%m-%d')
            
            # 1. Info Maestra
            v_data = next((v for v in self.vendors if v[0] == vid), None)
            info = {
                "ID Vendedor": vid,
                "Nombre": v_data[1],
                "Sucursal": v_data[2],
                "Provincia": v_data[3],
                "Periodo": f"Del {since} al {until}"
            }
            
            # 2. Stats
            stats_raw = self.controller.get_vendor_stats(vid)
            stats = {
                "Ventas Realizadas": f"{stats_raw['ventas']} facturas",
                "Ingresos Generados": f"RD$ {stats_raw['total_neto']:,.2f}",
                "Ganancia Neta (Margen)": f"RD$ {stats_raw['ganancia']:,.2f}"
            }
            
            # 3. Historial
            history = self.controller.get_vendor_sales_history(vid, since, until)
            
            filename = f"Ficha_Vendedor_{vid}_{datetime.now().strftime('%Y%m%d')}.pdf"
            ok, msg = PrintEngine.generate_vendor_comprehensive_report(
                f"Ficha Integral de Desempeño: {v_data[1]}",
                info,
                v_data[4], # URL de Foto
                stats,
                history,
                filename
            )
            
            if ok: messagebox.showinfo("Exito", msg)
            else: messagebox.showerror("Error", msg)
            
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", str(e))

    def build_products_tab(self):
        frm = self.tab_products
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        card_ind = self._create_card(frm, "📄 Ficha de Producto", 0, 0)
        self.products = self.prod_ctrl.get_all() 
        vals = [f"{p[0]} - {p[1]}" for p in self.products]
        self.cmb_prod = ctk.CTkComboBox(card_ind, values=vals, width=250)
        self.cmb_prod.pack(pady=10)
        ctk.CTkButton(card_ind, text="Ficha Técnica (PDF)", command=self.gen_product_profile, fg_color=Colors.PRIMARY).pack(pady=10)
        card_cat = self._create_card(frm, "🖼️ Catálogo Visual", 0, 1)
        ctk.CTkButton(card_cat, text="Generar Catálogo PDF", command=self.gen_product_catalog).pack(pady=10)

    def build_inventory_tab(self):
        frm = self.tab_inventory
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        
        # --- Card 1: Valoracion y Finanzas ---
        card_val = self._create_card(frm, "💰 Valoración de Capital", 0, 0)
        ctk.CTkLabel(card_val, text="Calcula el valor total del inventario a precio de costo\ny venta para determinar el capital estancado.").pack(pady=10)
        
        btn_box1 = ctk.CTkFrame(card_val, fg_color="transparent")
        btn_box1.pack(pady=10)
        ctk.CTkButton(btn_box1, text="🧮 Valoracion en Pantalla", command=self.show_inv_val, width=180).pack(side="left", padx=5)
        ctk.CTkButton(btn_box1, text="📄 Reporte Detallado PDF", command=self.gen_inv_valuation_pdf, fg_color=Colors.DANGER, width=180).pack(side="left", padx=5)
        
        self.lbl_inv_val = ctk.CTkLabel(card_val, text="", font=("Consolas", 14), justify="left")
        self.lbl_inv_val.pack(pady=10)

        # --- Card 2: Analisis de Rotacion (ABC) ---
        card_rot = self._create_card(frm, "🔄 Análisis de Rotación (ABC)", 0, 1)
        ctk.CTkLabel(card_rot, text="Clasifica productos por su velocidad de venta:\nClase A (Alta), B (Media) y C (Baja/Muerto).").pack(pady=10)
        ctk.CTkButton(card_rot, text="📊 Generar Analisis ABC (PDF)", command=self.gen_inv_rotation_pdf, fg_color=Colors.PRIMARY, height=40).pack(pady=15)

        # --- Card 3: Auditoria de Movimientos ---
        card_audit = self._create_card(frm, "🔍 Auditoría de Entradas/Salidas", 1, 0)
        
        date_frm = ctk.CTkFrame(card_audit, fg_color="transparent")
        date_frm.pack(pady=5)
        self.audit_since = DateEntry(date_frm, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.audit_since.grid(row=0, column=0, padx=5)
        self.audit_until = DateEntry(date_frm, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.audit_until.grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(card_audit, text="📜 Ver Auditoria Stock (PDF)", command=self.gen_inv_audit_pdf, fg_color="gray").pack(pady=10)

    def gen_inv_valuation_pdf(self):
        data = self.controller.get_inventory_valuation_detailed()
        cols = ["ID", "Producto", "Stock", "Costo U.", "Precio V.", "Val. Costo", "Val. Venta", "Margen Pot."]
        ok, msg = PrintEngine.generate_inventory_analytical_report("Reporte de Valoración de Inventario", data, cols, "VALORACION", "Valoracion_Inventario.pdf")
        if not ok: messagebox.showerror("Error", msg)

    def gen_inv_rotation_pdf(self):
        data = self.controller.get_inventory_rotation_analytics()
        cols = ["Producto", "Stock Actual", "Unid. Vendidas", "Clasificación ABC"]
        ok, msg = PrintEngine.generate_inventory_analytical_report("Análisis de Rotación de Inventario (ABC)", data, cols, "ABC", "Analisis_Rotacion_ABC.pdf")
        if not ok: messagebox.showerror("Error", msg)

    def gen_inv_audit_pdf(self):
        since = self.audit_since.get_date().strftime('%Y-%m-%d')
        until = self.audit_until.get_date().strftime('%Y-%m-%d')
        data = self.controller.get_inventory_movements_audit(since, until)
        if not data:
            messagebox.showinfo("Sin Datos", "No se encontraron movimientos en este rango.")
            return
        cols = ["Fecha/Hora", "Usuario", "Accion", "Producto", "Ant.", "Nuevo", "Dif."]
        ok, msg = PrintEngine.generate_inventory_analytical_report(f"Auditoría de Movimientos ({since} a {until})", data, cols, "AUDITORIA", "Auditoria_Inventario.pdf")
        if not ok: messagebox.showerror("Error", msg)

    def export_client_list(self):
        headers = ["ID", "Nombre", "Apellido", "RNC", "Tipo", "Direccion", "Credito", "Limite", "Region", "Provincia"]
        data = [[r[0], r[1], r[2], r[3], r[4], r[5], "SI" if r[6] else "NO", r[7], r[8], r[9]] for r in self.clients]
        ok, msg = self.controller.export_to_excel(data, headers, "Listado_Clientes.xlsx")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def gen_vendor_catalog(self):
        data, summary, date_narrative = self.controller.get_vendors_list_report()
        cols = ["ID", "Vendedor", "Sucursal", "Provincia", "Foto", "Ingresos", "Costos", "Margen", "%"]
        PrintEngine.generate_advanced_catalog_pdf("Reporte Vendedores", data, cols, summary, date_narrative, "Catalogo_Vendedores.pdf")

    def gen_vendor_profile(self):
        val = self.cmb_ven.get()
        if not val: return
        vid = int(val.split(" - ")[0])
        v_data = next((v for v in self.vendors if v[0] == vid), None)
        stats = self.controller.get_vendor_stats(vid)
        info = {"Nombre": v_data[1], "Sucursal": v_data[2], "Provincia": v_data[3], "ID": v_data[0]}
        stats_info = {"Vendido": f"${stats['total_neto']:,.2f}", "Ganancia": f"${stats['ganancia']:,.2f}"}
        PrintEngine.generate_profile_pdf(f"Ficha Vendedor: {v_data[1]}", info, v_data[4], stats_info, f"Vendedor_{vid}.pdf")

    def gen_product_catalog(self):
        data = self.controller.get_products_list_report()
        cols = ["ID", "Producto", "Stock", "Precio", "Foto"]
        PrintEngine.generate_catalog_pdf("Catalogo Productos", data, cols, "Catalogo_Productos.pdf")

    def gen_product_profile(self):
        val = self.cmb_prod.get()
        if not val: return
        pid = int(val.split(" - ")[0])
        p_data = next((p for p in self.products if p[0] == pid), None)
        margen = p_data[3] - p_data[5]
        margen_p = (margen / p_data[3] * 100) if p_data[3] > 0 else 0
        info = {"Producto": p_data[1], "Stock": p_data[2], "Precio": f"${p_data[3]:,.2f}"}
        stats = {"Costo": f"${p_data[5]:,.2f}", "Rentabilidad": f"{margen_p:.1f}%"}
        PrintEngine.generate_profile_pdf(f"Ficha Producto: {p_data[1]}", info, p_data[4], stats, f"Producto_{pid}.pdf")

    def show_inv_val(self):
        val = self.controller.get_inventory_valuation()
        txt = f"Unidades: {val[0]}\nCosto: ${val[1]:,.2f}\nVenta: ${val[2]:,.2f}\nMargen Potencial: ${val[3]:,.2f}"
        self.lbl_inv_val.configure(text=txt)
