import customtkinter as ctk
from tkinter import ttk
from src.views.styles import Colors, Fonts
from src.controllers.dashboard_controller import DashboardController
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = DashboardController()
        
        # Filtros Data
        self.filter_data = self.controller.get_filters_data()
        self.clients_map = {c['name']: c['id'] for c in self.filter_data['clients']}
        self.months_es = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # Grid Config
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1) # Chart area expands

        self.create_filters_bar()
        self.create_kpi_cards()
        self.create_charts_area()
        
        # Cargar todo (Histórico por defecto)
        self.refresh_data()

    def create_filters_bar(self):
        bar = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=50)
        bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Título
        ctk.CTkLabel(bar, text="📊 DASHBOARD EJECUTIVO", font=Fonts.TITLE, text_color=Colors.PRIMARY).pack(side="left", padx=15)

        # Botón Reset
        ctk.CTkButton(bar, text="🔄 Reset / Histórico", width=120, fg_color=Colors.HOVER, text_color="black", 
                      command=self.reset_filters).pack(side="right", padx=10)

        # Filtros (Derecha a Izquierda)
        # Cliente
        self.cb_client = ctk.CTkComboBox(bar, values=["Todos"] + list(self.clients_map.keys()), width=200, command=self.on_filter_change)
        self.cb_client.pack(side="right", padx=5)
        ctk.CTkLabel(bar, text="Cliente:").pack(side="right", padx=2)

        # Mes
        self.cb_month = ctk.CTkComboBox(bar, values=self.months_es, width=120, command=self.on_filter_change)
        self.cb_month.pack(side="right", padx=5)
        ctk.CTkLabel(bar, text="Mes:").pack(side="right", padx=2)

        # Año
        years = ["Todos"] + self.filter_data['years']
        self.cb_year = ctk.CTkComboBox(bar, values=years, width=100, command=self.on_filter_change)
        self.cb_year.pack(side="right", padx=5)
        ctk.CTkLabel(bar, text="Año:").pack(side="right", padx=2)

    def create_kpi_cards(self):
        # Frame KPIs (2 filas)
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.kpi_frame.columnconfigure((0,1,2,3), weight=1)
        
        # Row 1
        self.lbl_rev = self._card(0, 0, "Ingresos", "💰", Colors.SUCCESS)
        self.lbl_cost = self._card(0, 1, "Costos", "📉", Colors.DANGER)
        self.lbl_marg = self._card(0, 2, "Margen", "📈", Colors.PRIMARY)
        self.lbl_marg_pct = self._card(0, 3, "% Margen", "📊", "#F57C00")
        
        # Row 2
        self.lbl_trans = self._card(1, 0, "Transacciones", "🧾", "#5C6BC0")
        self.lbl_units = self._card(1, 1, "Unidades", "📦", "#26A69A")
        self.lbl_ticket = self._card(1, 2, "Ticket Prom.", "🏷️", "#7E57C2")
        self.lbl_status = self._card(1, 3, "Estado", "✅", "#78909C")

    def _card(self, row, col, title, icon, color):
        f = ctk.CTkFrame(self.kpi_frame, fg_color=color, corner_radius=6)
        f.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(f, text=f"{icon} {title}", font=("Arial", 11, "bold"), text_color="white").pack(pady=(5,0))
        l = ctk.CTkLabel(f, text="...", font=("Arial", 18, "bold"), text_color="white")
        l.pack(pady=(0,5))
        return l

    def create_charts_area(self):
        main_frm = ctk.CTkFrame(self, fg_color="transparent")
        main_frm.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        main_frm.columnconfigure(0, weight=3) # Chart bigger
        main_frm.columnconfigure(1, weight=2) # Table smaller
        main_frm.rowconfigure(0, weight=1)

        # --- Chart ---
        chart_pnl = ctk.CTkFrame(main_frm, fg_color=Colors.PANEL)
        chart_pnl.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        ctk.CTkLabel(chart_pnl, text="Tendencia de Ventas (Selección)", font=Fonts.SUBTITLE).pack(pady=5)
        
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(Colors.PANEL)
        self.ax.set_facecolor(Colors.PANEL)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_pnl)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # --- Table ---
        tbl_pnl = ctk.CTkFrame(main_frm, fg_color=Colors.PANEL)
        tbl_pnl.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        
        ctk.CTkLabel(tbl_pnl, text="🏆 Top Productos (Volumen)", font=Fonts.SUBTITLE).pack(pady=5)
        
        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Roboto', 10, 'bold'), background=Colors.PRIMARY, foreground="white")
        style.configure("Treeview", font=('Roboto', 10), rowheight=25, background="white", fieldbackground="white")
        style.map("Treeview", background=[('selected', Colors.HOVER)], foreground=[('selected', 'black')])

        cols = ("Producto", "Qty", "Total")
        self.tree = ttk.Treeview(tbl_pnl, columns=cols, show="headings")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Qty", text="Cant.")
        self.tree.heading("Total", text="Total ($)")
        
        self.tree.column("Producto", width=150)
        self.tree.column("Qty", width=50, anchor="center")
        self.tree.column("Total", width=80, anchor="e")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def reset_filters(self):
        self.cb_year.set("Todos")
        self.cb_month.set("Todos")
        self.cb_client.set("Todos")
        self.refresh_data()

    def on_filter_change(self, choice):
        self.refresh_data()

    def refresh_data(self):
        # Refresh Filters Data first (in case of new clients/sales)
        threading.Thread(target=self._refresh_filters_and_data, daemon=True).start()

    def _refresh_filters_and_data(self):
        # 1. Update Filters Data
        new_filter_data = self.controller.get_filters_data()
        
        # 2. Get current selection params
        y = self.cb_year.get()
        m = self.cb_month.get()
        c_name = self.cb_client.get()
        c_id = self.clients_map.get(c_name)

        # 3. Update internal maps and lists (Main Thread safe update later)
        self.filter_data = new_filter_data
        self.clients_map = {c['name']: c['id'] for c in self.filter_data['clients']}
        new_years = ["Todos"] + self.filter_data['years']
        new_clients = ["Todos"] + list(self.clients_map.keys())

        # 4. Fetch Data
        kpis = self.controller.get_kpis(y, m, c_id)
        chart_d, top_p = self.controller.get_charts_data(y, m, c_id)
        
        self.after(0, lambda: self._update_ui_full(kpis, chart_d, top_p, new_years, new_clients))

    def _update_ui_full(self, kpis, chart_data, top_products, new_years, new_clients):
        if not self.winfo_exists(): return
        
        # Update Combo Values silently maintaining selection if valid
        cur_y = self.cb_year.get()
        cur_c = self.cb_client.get()
        
        self.cb_year.configure(values=new_years)
        if cur_y in new_years: self.cb_year.set(cur_y)
        
        self.cb_client.configure(values=new_clients)
        if cur_c in new_clients: self.cb_client.set(cur_c)

        # Call standard UI update
        self._update_ui(kpis, chart_data, top_products)

    def _update_ui(self, kpis, chart_data, top_products):
        if not self.winfo_exists(): return
        
        if not kpis: return # Error handling

        # Update KPIs
        self.lbl_rev.configure(text=f"${kpis['ingresos']:,.0f}")
        self.lbl_cost.configure(text=f"${kpis['costos']:,.0f}")
        self.lbl_marg.configure(text=f"${kpis['margen']:,.0f}")
        self.lbl_marg_pct.configure(text=f"{kpis['margen_pct']:.1f}%")
        self.lbl_trans.configure(text=str(kpis['transacciones']))
        self.lbl_units.configure(text=str(kpis['unidades']))
        self.lbl_ticket.configure(text=f"${kpis['ticket_promedio']:,.0f}")
        self.lbl_status.configure(text="OK")

        # Update Chart
        days, vals = chart_data
        self.ax.clear()
        if days:
            # Area Chart Effect
            self.ax.fill_between(days, vals, color=Colors.PRIMARY, alpha=0.3)
            self.ax.plot(days, vals, color=Colors.PRIMARY, marker='o')
            
            # Formato
            self.ax.tick_params(colors=Colors.TEXT, rotation=45, labelsize=8)
            self.ax.grid(True, linestyle='--', alpha=0.5)
            for s in self.ax.spines.values(): s.set_visible(False)
        else:
            self.ax.text(0.5, 0.5, "Sin datos para este filtro", ha='center')
        self.fig.tight_layout()
        self.canvas.draw()

        # Update Table
        for i in self.tree.get_children(): self.tree.delete(i)
        for i, p in enumerate(top_products):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(p[0], p[1], f"${p[2]:,.0f}"), tags=(tag,))
        
        # Zebra Striping
        self.tree.tag_configure('odd', background=Colors.BACKGROUND)
        self.tree.tag_configure('even', background="white")