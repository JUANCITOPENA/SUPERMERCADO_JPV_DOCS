
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from src.views.styles import Colors, Fonts
from src.controllers.sales_controller import SalesController
from src.utils.print_engine import PrintEngine

class SalesHistoryView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = SalesController()
        self.user_data = user_data
        
        self.create_header()
        self.create_grid()
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Historial de Ventas", font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=20)
        
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Buscar (Cliente/NCF)...", width=250)
        self.entry_search.pack(side="left", padx=10)
        
        # Simple date filter placeholders (in a real app, use DatePicker widget)
        self.ent_from = ctk.CTkEntry(header, placeholder_text="YYYY-MM-DD (Desde)", width=120)
        self.ent_from.pack(side="left", padx=5)
        
        self.ent_to = ctk.CTkEntry(header, placeholder_text="YYYY-MM-DD (Hasta)", width=120)
        self.ent_to.pack(side="left", padx=5)
        
        ctk.CTkButton(header, text="Filtrar", command=self.apply_filters, width=80).pack(side="left", padx=10)
        
        # Actions
        ctk.CTkButton(header, text="Reimprimir", fg_color=Colors.PRIMARY, command=self.reprint_ticket).pack(side="right", padx=10)
        
        if self.user_data['rol'] == 'admin':
            ctk.CTkButton(header, text="Anular Venta", fg_color=Colors.DANGER, command=self.cancel_sale).pack(side="right", padx=10)
            
        ctk.CTkButton(header, text="Ver Detalle", fg_color="gray", command=self.show_detail).pack(side="right", padx=10)

    def create_grid(self):
        self.tree = ttk.Treeview(self, columns=("ID", "Fecha", "Cliente", "NCF", "Total", "Vendedor", "Estado"), show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50)
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.column("Cliente", width=200)
        self.tree.heading("NCF", text="NCF")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Vendedor", text="Vendedor")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self, filters=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.controller.get_all_sales(filters)
        for row in data:
            # row: ID, FECHA, CLIENTE, NCF, TOTAL, ESTADO, VENDEDOR
            date_str = row[1].strftime("%Y-%m-%d %H:%M") if row[1] else ""
            self.tree.insert("", "end", values=(row[0], date_str, row[2], row[3], f"{row[4]:,.2f}", row[6], row[5]))

    def apply_filters(self):
        f = {
            "search": self.entry_search.get(),
            "date_from": self.ent_from.get(),
            "date_to": self.ent_to.get()
        }
        self.load_data(f)

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel: return None
        return self.tree.item(sel[0])['values'][0]

    def show_detail(self):
        sid = self.get_selected_id()
        if not sid: return
        
        head, items = self.controller.get_sale_full_detail(sid)
        if not head: return
        
        txt = f"Cliente: {head['client_name']}\nNCF: {head['ncf']}\n\nProductos:\n"
        for i in items:
            txt += f"- {i['name']} x{i['qty']} | ${i['total']:,.2f}\n"
        txt += f"\nTotal: ${head['total']:,.2f}"
        
        messagebox.showinfo(f"Detalle Venta #{sid}", txt)

    def reprint_ticket(self):
        sid = self.get_selected_id()
        if not sid: return
        
        head, items = self.controller.get_sale_full_detail(sid)
        if not head: return
        
        try:
            PrintEngine.generate_invoice(head, items, is_copy=True, user_reprint=self.user_data['username'])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancel_sale(self):
        sid = self.get_selected_id()
        if not sid: return
        
        if messagebox.askyesno("Confirmar Anulación", "ADVERTENCIA: Esta acción retornará el stock y marcará la venta como cancelada.\n¿Continuar?"):
            ok, msg = self.controller.cancel_sale(sid)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.load_data()
            else:
                messagebox.showerror("Error", msg)
