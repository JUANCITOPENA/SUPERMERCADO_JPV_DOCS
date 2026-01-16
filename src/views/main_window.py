
import customtkinter as ctk
from src.views.styles import Colors, Fonts
from src.views.pos import PosView
from src.views.clients import ClientsView
from src.views.products import ProductsView
from src.views.sellers import SellersView
from src.views.reports import ReportsView
from src.views.sales_history import SalesHistoryView
from src.views.users import UsersView
from src.views.aux_masters import AuxMastersView
from src.views.dashboard import DashboardView

class MainWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        self.title(f"🏢 MINI ERP SUPERMERCADO V6 - Usuario: {user_data['username']} ({user_data['rol']})")
        
        # Center Window Logic
        w, h = 1280, 768
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.minsize(1024, 600)
        
        self.configure(fg_color=Colors.BACKGROUND)

        # Layout: Grid 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.create_sidebar()

        # Content Area
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=Colors.BACKGROUND)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Default View
        self.show_dashboard()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=Colors.PANEL)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1) # Spacer

        self.logo_label = ctk.CTkLabel(self.sidebar, text="🏢 MINI ERP\nJPV V6", font=Fonts.TITLE, text_color=Colors.TEXT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.create_nav_button("📊 Dashboard", self.show_dashboard, 1)
        self.create_nav_button("🛒 Punto de Venta", self.show_pos, 2)
        self.create_nav_button("📜 Historial Ventas", self.show_history, 3)
        
        # Separator
        ttk_sep = ctk.CTkLabel(self.sidebar, text="📁 --- MAESTROS ---", text_color="gray")
        ttk_sep.grid(row=4, column=0, pady=5)
        
        self.create_nav_button("👥 Clientes", self.show_clients, 5)
        self.create_nav_button("📦 Productos", self.show_products, 6)
        self.create_nav_button("👔 Vendedores", self.show_sellers, 7)
        
        if self.user_data['rol'] == 'admin':
            self.create_nav_button("🛡️ Usuarios", self.show_users, 8)
            self.create_nav_button("🧩 Maestros Auxiliares", self.show_aux, 9)
            self.create_nav_button("📊 Reportes Avanzados", self.show_reports, 10)
        
        # Spacer
        self.btn_logout = ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", fg_color=Colors.DANGER, command=self.logout)
        self.btn_logout.grid(row=12, column=0, padx=20, pady=20)

    def create_nav_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                            fg_color="transparent", text_color=Colors.TEXT, hover_color=Colors.HOVER, 
                            anchor="w", height=40, font=Fonts.BUTTON)
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        return btn

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        DashboardView(self.content_frame).pack(fill="both", expand=True)

    def show_pos(self):
        self.clear_content()
        PosView(self.content_frame, self.user_data).pack(fill="both", expand=True)


    def show_history(self):
        self.clear_content()
        SalesHistoryView(self.content_frame, self.user_data).pack(fill="both", expand=True)

    def show_clients(self):
        self.clear_content()
        ClientsView(self.content_frame, self.user_data).pack(fill="both", expand=True)

    def show_products(self):
        self.clear_content()
        ProductsView(self.content_frame, self.user_data).pack(fill="both", expand=True)
    
    def show_sellers(self):
        self.clear_content()
        SellersView(self.content_frame, self.user_data).pack(fill="both", expand=True)
    
    def show_users(self):
        self.clear_content()
        UsersView(self.content_frame, self.user_data).pack(fill="both", expand=True)

    def show_reports(self):
        self.clear_content()
        ReportsView(self.content_frame).pack(fill="both", expand=True)

    def show_aux(self):
        self.clear_content()
        AuxMastersView(self.content_frame).pack(fill="both", expand=True)

    def logout(self):
        self.destroy()
