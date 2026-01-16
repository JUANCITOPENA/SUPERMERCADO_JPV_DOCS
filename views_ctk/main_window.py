
import customtkinter as ctk
from views_ctk.styles import Colors, Fonts
from views_ctk.pos import PosView
from views_ctk.clients import ClientsView
from views_ctk.products import ProductsView
from views_ctk.sellers import SellersView
from views_ctk.reports import ReportsView
from views_ctk.sales_history import SalesHistoryView
from views_ctk.users import UsersView

class MainWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        self.title(f"MINI ERP SUPERMERCADO V6 - Usuario: {user_data['username']} ({user_data['rol']})")
        self.geometry("1280x768")
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
        self.show_pos()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=Colors.PANEL)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1) # Spacer

        self.logo_label = ctk.CTkLabel(self.sidebar, text="MINI ERP\nJPV V6", font=Fonts.TITLE, text_color=Colors.TEXT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.create_nav_button("Punto de Venta", self.show_pos, 1)
        self.create_nav_button("Historial Ventas", self.show_history, 2)
        
        # Separator
        ttk_sep = ctk.CTkLabel(self.sidebar, text="--- MAESTROS ---", text_color="gray")
        ttk_sep.grid(row=3, column=0, pady=5)
        
        self.create_nav_button("Clientes", self.show_clients, 4)
        self.create_nav_button("Productos", self.show_products, 5)
        self.create_nav_button("Vendedores", self.show_sellers, 6)
        
        if self.user_data['rol'] == 'admin':
            self.create_nav_button("Usuarios", self.show_users, 7)
            self.create_nav_button("Reportes Avanzados", self.show_reports, 8)
        
        # Spacer
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color=Colors.DANGER, command=self.logout)
        self.btn_logout.grid(row=10, column=0, padx=20, pady=20)

    def create_nav_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                            fg_color="transparent", text_color=Colors.TEXT, hover_color=Colors.HOVER, 
                            anchor="w", height=40, font=Fonts.BUTTON)
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        return btn

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

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

    def logout(self):
        self.destroy()
