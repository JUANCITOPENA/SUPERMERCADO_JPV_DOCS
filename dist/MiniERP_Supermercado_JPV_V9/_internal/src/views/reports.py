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
            # Filter by type manually from data rows if needed (data[6] is type)
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

    # --- REST OF METHODS (Unchanged but ensuring consistency) ---
    def build_clients_tab(self):
        frm = self.tab_clients
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        card_ind = self._create_card(frm, "📄 Reporte Individual", 0, 0)
        self.clients = self.cli_ctrl.get_all()
        vals = [f"{c[0]} - {c[1]} {c[2]}" for c in self.clients]
        self.cmb_cli = ctk.CTkComboBox(card_ind, values=vals, width=250)
        self.cmb_cli.pack(pady=10)
        ctk.CTkButton(card_ind, text="Generar Perfil PDF", command=self.gen_client_pdf, fg_color=Colors.PRIMARY).pack(pady=5)
        ctk.CTkButton(card_ind, text="Estado de Cuenta (PDF)", command=self.gen_client_statement, fg_color=Colors.DANGER).pack(pady=5)
        self.lbl_cli_stats = ctk.CTkLabel(card_ind, text="Seleccione cliente...")
        self.lbl_cli_stats.pack(pady=10)
        card_gen = self._create_card(frm, "📑 Listado General", 0, 1)
        ctk.CTkButton(card_gen, text="Exportar Lista de Clientes (Excel)", command=self.export_client_list, fg_color=Colors.SUCCESS).pack(pady=10)

    def build_vendors_tab(self):
        frm = self.tab_vendors
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        card_ind = self._create_card(frm, "📄 Ficha de Vendedor", 0, 0)
        self.vendors = self.ven_ctrl.get_all() 
        vals = [f"{v[0]} - {v[1]}" for v in self.vendors]
        self.cmb_ven = ctk.CTkComboBox(card_ind, values=vals, width=250)
        self.cmb_ven.pack(pady=10)
        ctk.CTkButton(card_ind, text="Generar Ficha con Foto (PDF)", command=self.gen_vendor_profile, fg_color=Colors.PRIMARY).pack(pady=10)
        card_cat = self._create_card(frm, "📚 Catálogo de Vendedores", 0, 1)
        ctk.CTkButton(card_cat, text="Generar Catálogo PDF", command=self.gen_vendor_catalog).pack(pady=10)

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
        card = self._create_card(frm, "💰 Análisis Financiero", 0, 0)
        card.pack(fill="both", padx=20, pady=20)
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_box := ctk.CTkFrame(card, fg_color="transparent"), text="Calcular Valoración", command=self.show_inv_val).pack(side="left", padx=10)
        btn_box.pack()
        self.lbl_inv_val = ctk.CTkLabel(card, text="", font=("Consolas", 16))
        self.lbl_inv_val.pack(pady=20)

    def export_client_list(self):
        headers = ["ID", "Nombre", "Apellido", "RNC", "Tipo", "Direccion", "Credito", "Limite", "Region", "Provincia"]
        data = [[r[0], r[1], r[2], r[3], r[4], r[5], "SI" if r[6] else "NO", r[7], r[8], r[9]] for r in self.clients]
        ok, msg = self.controller.export_to_excel(data, headers, "Listado_Clientes.xlsx")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def gen_client_pdf(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        stats = self.controller.get_client_stats(cid)
        c_data = next((c for c in self.clients if c[0] == cid), None)
        info = {"Nombre": f"{c_data[1]} {c_data[2]}", "RNC": c_data[3], "Tipo": c_data[4], "Provincia": c_data[9]}
        stats_info = {"Total Comprado": f"${stats['venta']:,.2f}", "Margen": f"${stats['margen_moneda']:,.2f}", "Rentabilidad": f"{stats['margen_porc']:.1f}%"}
        PrintEngine.generate_profile_pdf(f"Perfil Cliente: {c_data[1]}", info, None, stats_info, f"Cliente_{cid}.pdf")

    def gen_client_statement(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        data = self.controller.get_client_account_statement(cid)
        ok, msg = PrintEngine.generate_account_statement_pdf(data, f"Estado_Cuenta_Cliente_{cid}.pdf")
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
