import customtkinter as ctk
from tkinter import messagebox
from src.views.styles import Colors, Fonts
from src.controllers.report_controller import ReportController
from src.controllers.client_controller import ClientController
from src.controllers.vendor_controller import VendorController
from src.controllers.products_controller import ProductController
from src.utils.print_engine import PrintEngine

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
        self.tab_inventory = self.tabview.add("📋 Inventario")
        
        self.build_clients_tab()
        self.build_vendors_tab()
        self.build_products_tab()
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
        
        # Individual Card
        card_ind = self._create_card(frm, "📄 Reporte Individual", 0, 0)
        
        self.clients = self.cli_ctrl.get_all()
        vals = [f"{c[0]} - {c[1]} {c[2]}" for c in self.clients]
        self.cmb_cli = ctk.CTkComboBox(card_ind, values=vals, width=250)
        self.cmb_cli.pack(pady=10)
        
        ctk.CTkButton(card_ind, text="Generar Perfil PDF", command=self.gen_client_pdf, fg_color=Colors.PRIMARY).pack(pady=5)
        ctk.CTkButton(card_ind, text="Estado de Cuenta (PDF)", command=self.gen_client_statement, fg_color=Colors.DANGER).pack(pady=5)
        ctk.CTkButton(card_ind, text="Ver Stats en Pantalla", command=self.load_client_stats, fg_color="gray").pack(pady=5)
        self.lbl_cli_stats = ctk.CTkLabel(card_ind, text="Seleccione cliente...")
        self.lbl_cli_stats.pack(pady=10)

        # General Card
        card_gen = self._create_card(frm, "📑 Listado General", 0, 1)
        ctk.CTkLabel(card_gen, text="Genera una lista maestra de todos los clientes\ncon su estatus de crédito y contacto.").pack(pady=20)
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
        ctk.CTkLabel(card_cat, text="Lista de vendedores con miniaturas de fotos.").pack(pady=20)
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
        ctk.CTkLabel(card_cat, text="Lista de productos con foto, precio y stock.").pack(pady=20)
        ctk.CTkButton(card_cat, text="Generar Catálogo PDF", command=self.gen_product_catalog).pack(pady=10)
        ctk.CTkButton(card_cat, text="Reporte Rendimiento (PDF + Gráfico)", command=self.gen_product_performance, fg_color=Colors.SUCCESS).pack(pady=10)

    def build_inventory_tab(self):
        frm = self.tab_inventory
        card = self._create_card(frm, "💰 Análisis Financiero", 0, 0)
        card.pack(fill="both", padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Calcular Valoración", command=self.show_inv_val).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Exportar Excel Rentabilidad", command=self.export_rentability, fg_color=Colors.SUCCESS).pack(side="left", padx=10)
        
        self.lbl_inv_val = ctk.CTkLabel(card, text="", font=("Consolas", 16))
        self.lbl_inv_val.pack(pady=20)

    def load_client_stats(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        stats = self.controller.get_client_stats(cid)
        txt = (f"Compras: {stats['compras']} | Total: ${stats['venta']:,.2f}\n"
               f"Margen: ${stats['margen_moneda']:,.2f} ({stats['margen_porc']:.1f}%)")
        self.lbl_cli_stats.configure(text=txt)

    def gen_client_pdf(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        stats = self.controller.get_client_stats(cid)
        
        c_data = next((c for c in self.clients if c[0] == cid), None)
        # c_data: ID, Nom, Ape, RNC, Tipo, Dir, Cred, Lim, RegName, ProvName...
        
        info = {
            "Nombre": f"{c_data[1]} {c_data[2]}",
            "RNC/Cédula": c_data[3],
            "Tipo": c_data[4],
            "Provincia": c_data[9]
        }
        
        stats_info = {
            "Total Comprado": f"${stats['venta']:,.2f}",
            "Margen Bruto": f"${stats['margen_moneda']:,.2f}",
            "Rentabilidad": f"{stats['margen_porc']:.1f}%"
        }
        # Clients don't have images in the DB schema provided, so None
        PrintEngine.generate_profile_pdf(f"Perfil de Cliente: {c_data[1]}", info, None, stats_info, f"Cliente_{cid}.pdf")

    def gen_client_statement(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        
        data = self.controller.get_client_account_statement(cid)
        # data contains: client_name, client_rnc, client_addr, transactions, final_balance
        
        ok, msg = PrintEngine.generate_account_statement_pdf(data, f"Estado_Cuenta_Cliente_{cid}.pdf")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def export_client_excel(self):
        val = self.cmb_cli.get()
        if not val: return
        cid = int(val.split(" - ")[0])
        history = self.controller.get_client_history(cid)
        headers = ["ID Venta", "Fecha", "NCF", "Total", "Items"]
        ok, msg = self.controller.export_to_excel(history, headers, f"Historial_Cliente_{cid}.xlsx")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def export_client_list(self):
        # Exports all clients to excel
        # self.clients contains: ID, Nom, Ape, RNC, Tipo, Dir, Cred, Lim, Reg, Prov, id_reg, id_prov
        headers = ["ID", "Nombre", "Apellido", "RNC", "Tipo", "Direccion", "Credito", "Limite", "Region", "Provincia"]
        data = []
        for row in self.clients:
            # Filter cols
            new_row = [row[0], row[1], row[2], row[3], row[4], row[5], "SI" if row[6] else "NO", row[7], row[8], row[9]]
            data.append(new_row)
            
        ok, msg = self.controller.export_to_excel(data, headers, "Listado_Clientes.xlsx")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)

    def gen_product_performance(self):
        data = self.controller.get_product_performance_stats()
        # Data cols: Prod, Qty, Rev, Cost, Marg, Marg%
        cols = ["Producto", "Cant", "Ingresos", "Costos", "Margen $", "Margen %"]
        
        ok, msg = PrintEngine.generate_performance_pdf("Rendimiento de Productos", data, cols, "Reporte_Rendimiento.pdf")
        if ok: messagebox.showinfo("Info", msg)
        else: messagebox.showerror("Error", msg)

    def gen_vendor_catalog(self):
        data, summary, date_narrative = self.controller.get_vendors_list_report()
        cols = ["ID", "Vendedor", "Sucursal", "Provincia", "Foto", "Ingresos", "Costos", "Margen", "%"]
        
        ok, msg = PrintEngine.generate_advanced_catalog_pdf(
            "Reporte General de Vendedores", 
            data, 
            cols, 
            summary, 
            date_narrative, 
            "Catalogo_Vendedores_Financiero.pdf"
        )
        if ok: messagebox.showinfo("Info", msg)
        else: messagebox.showerror("Error", msg)

    def gen_vendor_profile(self):
        val = self.cmb_ven.get()
        if not val: return
        vid = int(val.split(" - ")[0])
        v_data = next((v for v in self.vendors if v[0] == vid), None)
        stats = self.controller.get_vendor_stats(vid)
        
        info = {
            "Nombre": v_data[1],
            "Sucursal": v_data[2],
            "Provincia": v_data[3],
            "ID Vendedor": v_data[0]
        }
        stats_info = {
            "Monto Vendido": f"${stats['total_neto']:,.2f}",
            "Ganancia Generada": f"${stats['ganancia']:,.2f}"
        }
        PrintEngine.generate_profile_pdf(f"Ficha Vendedor: {v_data[1]}", info, v_data[4], stats_info, f"Vendedor_{vid}.pdf")

    def gen_product_catalog(self):
        data = self.controller.get_products_list_report()
        cols = ["ID", "Producto", "Stock", "Precio Venta", "Foto"]
        PrintEngine.generate_catalog_pdf("Catálogo de Productos", data, cols, "Catalogo_Productos.pdf")

    def gen_product_profile(self):
        val = self.cmb_prod.get()
        if not val: return
        pid = int(val.split(" - ")[0])
        p_data = next((p for p in self.products if p[0] == pid), None)
        margen = p_data[3] - p_data[5]
        margen_p = (margen / p_data[3] * 100) if p_data[3] > 0 else 0
        
        info = {
            "Producto": p_data[1],
            "Stock": p_data[2],
            "Precio": f"${p_data[3]:,.2f}"
        }
        stats = {
            "Costo": f"${p_data[5]:,.2f}",
            "Rentabilidad": f"{margen_p:.1f}%"
        }
        PrintEngine.generate_profile_pdf(f"Ficha Producto: {p_data[1]}", info, p_data[4], stats, f"Producto_{pid}.pdf")

    def show_inv_val(self):
        val = self.controller.get_inventory_valuation()
        val = [v if v else 0 for v in val]
        txt = (f"Unidades Totales: {val[0]}\n"
               f"Inversión (Costo): ${val[1]:,.2f}\n"
               f"Valor Venta: ${val[2]:,.2f}\n"
               f"Margen Potencial: ${val[3]:,.2f}")
        self.lbl_inv_val.configure(text=txt)

    def export_rentability(self):
        data = self.controller.get_product_rentability()
        headers = ["ID", "Producto", "Costo", "Precio", "Margen $", "Margen %"]
        ok, msg = self.controller.export_to_excel(data, headers, "Rentabilidad.xlsx")
        if ok: messagebox.showinfo("OK", msg)
        else: messagebox.showerror("Error", msg)
