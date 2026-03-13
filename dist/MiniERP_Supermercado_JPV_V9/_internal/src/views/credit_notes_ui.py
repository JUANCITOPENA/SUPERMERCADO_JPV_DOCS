import customtkinter as ctk
from tkinter import ttk, messagebox
from src.controllers.credit_note_controller import CreditNoteController
from src.views.styles import Colors, Fonts
from src.utils.print_engine import PrintEngine
from datetime import datetime
from tkcalendar import DateEntry
import traceback

class CreditNotesView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color="transparent")
        self.user_data = user_data
        self.controller = CreditNoteController()
        
        self.init_ui()

    def init_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=70)
        header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(header, text="📑 HISTORIAL DE NOTAS DE CRÉDITO (E34)", font=Fonts.TITLE).pack(side="left", padx=20)
        
        self.btn_new = ctk.CTkButton(header, text="+ Nueva Nota de Crédito", fg_color=Colors.SUCCESS, 
                                    font=Fonts.BUTTON, height=40, command=self.open_new_nc_window)
        self.btn_new.pack(side="right", padx=20, pady=10)

        # Filters Area
        filter_frm = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        filter_frm.pack(fill="x", padx=10, pady=5)

        # 1. Multi-criteria Search
        search_sub = ctk.CTkFrame(filter_frm, fg_color="transparent")
        search_sub.pack(side="left", padx=10, pady=15)
        
        ctk.CTkLabel(search_sub, text="Buscar:", font=Fonts.BODY).pack(side="left", padx=5)
        self.ent_search = ctk.CTkEntry(search_sub, width=250, placeholder_text="NCF, Cliente o ID...")
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<Return>", lambda e: self.refresh_main_grid())

        # 2. Date Range with Pickers
        date_sub = ctk.CTkFrame(filter_frm, fg_color="transparent")
        date_sub.pack(side="left", padx=20)
        
        ctk.CTkLabel(date_sub, text="Desde:", font=Fonts.BODY).pack(side="left", padx=5)
        self.cal_since = DateEntry(date_sub, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal_since.pack(side="left", padx=5)
        
        ctk.CTkLabel(date_sub, text="Hasta:", font=Fonts.BODY).pack(side="left", padx=5)
        self.cal_until = DateEntry(date_sub, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal_until.pack(side="left", padx=5)

        # 3. Filter Button (Explicitly visible)
        self.btn_filter = ctk.CTkButton(filter_frm, text="🔍 APLICAR FILTROS", width=150, height=35,
                                       fg_color=Colors.PRIMARY, command=self.refresh_main_grid)
        self.btn_filter.pack(side="left", padx=20)

        # Main Grid
        grid_frm = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        grid_frm.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(grid_frm, text="💡 Doble clic sobre un registro para REIMPRIMIR el PDF", font=("Arial", 10, "italic"), text_color="gray").pack(anchor="e", padx=15)

        cols = ("ID", "NCF Nota", "Referencia", "Cliente", "Fecha", "Motivo", "Monto")
        self.tree = ttk.Treeview(grid_frm, columns=cols, show="headings")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        
        self.tree.column("Cliente", width=220, anchor="w")
        self.tree.column("Motivo", width=250, anchor="w")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.reprint_nc)
        
        # Carga inicial
        self.after(100, self.refresh_main_grid)

    def refresh_main_grid(self):
        try:
            # Limpiar
            for i in self.tree.get_children(): self.tree.delete(i)
            
            criteria = self.ent_search.get()
            since = self.cal_since.get()
            until = self.cal_until.get()
            
            data = self.controller.list_credit_notes(criteria, since, until)
            
            if not data:
                print("No se encontraron notas de credito con los filtros actuales.")
                return

            for r in data:
                f_val = r['fecha']
                f_str = f_val.strftime("%Y-%m-%d %H:%M") if hasattr(f_val, 'strftime') else str(f_val)
                
                self.tree.insert("", "end", iid=r['id'], values=(
                    r['id'], r['ncf'], r['ref'], r['cliente'], 
                    f_str, r['motivo'], f"${r['total']:,.2f}"
                ))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al refrescar tabla: {e}")

    def reprint_nc(self, e):
        sel = self.tree.selection()
        if not sel: return
        id_nc = int(sel[0])
        
        nc_info, items = self.controller.get_nc_full_details(id_nc)
        if nc_info:
            PrintEngine.generate_credit_note(nc_info, items)
        else:
            messagebox.showerror("Error", "No se pudo recuperar la informacion de impresion.")

    def open_new_nc_window(self):
        NewCreditNoteWindow(self, self.user_data, self.refresh_main_grid)

class NewCreditNoteWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_data, callback):
        super().__init__(parent)
        self.user_data = user_data
        self.callback = callback
        self.controller = CreditNoteController()
        
        self.title("EMISIÓN DE NOTA DE CRÉDITO PROFESIONAL")
        self.geometry("1100x850")
        self.configure(fg_color=Colors.BACKGROUND)
        self.grab_set() 
        
        self.invoice_data = None
        self.nc_type = ctk.StringVar(value="PARCIAL") # "TOTAL" o "PARCIAL"
        
        self.init_ui()

    def init_ui(self):
        # --- PASO 1: LOCALIZAR FACTURA ---
        step1 = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        step1.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(step1, text="1. BUSCAR FACTURA ORIGINAL (NCF o Cliente):", font=Fonts.SUBTITLE).pack(side="left", padx=15, pady=15)
        self.ent_inv_search = ctk.CTkEntry(step1, width=400, placeholder_text="Escriba NCF o nombre del cliente...")
        self.ent_inv_search.pack(side="left", padx=10)
        self.ent_inv_search.bind("<Return>", lambda e: self.search_invoice())
        
        ctk.CTkButton(step1, text="BUSCAR", command=self.search_invoice, width=120, height=35).pack(side="left", padx=5)

        # Grid de facturas encontradas
        self.inv_tree = ttk.Treeview(self, columns=("ID", "NCF", "Cliente", "Total", "Fecha", "Estado"), show="headings", height=5)
        for c in ("ID", "NCF", "Cliente", "Total", "Fecha", "Estado"):
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=140, anchor="center")
        self.inv_tree.pack(fill="x", padx=20, pady=5)
        self.inv_tree.bind("<Double-1>", lambda e: self.load_invoice_details())

        # --- OPCIONES DE NOTA DE CREDITO ---
        self.mode_frm = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frm.pack(fill="x", padx=20, pady=10)
        self.mode_frm.pack_forget() # Oculto hasta elegir factura

        ctk.CTkLabel(self.mode_frm, text="TIPO DE NOTA DE CRÉDITO:", font=Fonts.BODY).pack(side="left", padx=10)
        
        self.rb_total = ctk.CTkRadioButton(self.mode_frm, text="ANULACIÓN TOTAL (Cancela todo)", 
                                          variable=self.nc_type, value="TOTAL", command=self.on_mode_change)
        self.rb_total.pack(side="left", padx=30)
        
        self.rb_partial = ctk.CTkRadioButton(self.mode_frm, text="DEVOLUCIÓN PARCIAL (Elegir productos)", 
                                            variable=self.nc_type, value="PARCIAL", command=self.on_mode_change)
        self.rb_partial.pack(side="left", padx=30)

        # --- PASO 2: DETALLE DE PRODUCTOS ---
        self.details_frm = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        self.details_frm.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_step2 = ctk.CTkLabel(self.details_frm, text="2. DETALLES DE LA OPERACIÓN:", font=Fonts.SUBTITLE)
        self.lbl_step2.pack(anchor="w", padx=15, pady=5)
        
        self.items_tree = ttk.Treeview(self.details_frm, columns=("ID", "Producto", "Vendidas", "Devolver", "Precio", "Subtotal"), show="headings")
        for c in ("ID", "Producto", "Vendidas", "Devolver", "Precio", "Subtotal"):
            self.items_tree.heading(c, text=c)
            self.items_tree.column(c, width=130, anchor="center")
        
        self.items_tree.column("Producto", width=300, anchor="w")
        self.items_tree.pack(fill="both", expand=True, padx=15, pady=5)
        self.items_tree.bind("<Double-1>", self.on_item_double_click)

        # --- PASO 3: MOTIVO Y CIERRE ---
        bottom = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        bottom.pack(fill="x", padx=20, pady=15)
        
        self.lbl_total_refund = ctk.CTkLabel(bottom, text="TOTAL A DEVOLVER: RD$ 0.00", font=("Arial", 24, "bold"), text_color=Colors.SUCCESS)
        self.lbl_total_refund.pack(side="left", padx=20, pady=15)
        
        self.ent_reason = ctk.CTkEntry(bottom, placeholder_text="Escriba el motivo de la NC aqui...", width=400, height=40)
        self.ent_reason.pack(side="left", padx=20)
        
        self.btn_save = ctk.CTkButton(bottom, text="✅ PROCESAR Y GENERAR PDF", fg_color=Colors.SUCCESS, 
                                     height=55, width=200, font=Fonts.BUTTON, state="disabled", command=self.process_final)
        self.btn_save.pack(side="right", padx=20)

    def search_invoice(self):
        for i in self.inv_tree.get_children(): self.inv_tree.delete(i)
        res = self.controller.search_invoices(self.ent_inv_search.get())
        for r in res:
            self.inv_tree.insert("", "end", iid=r['id_venta'], values=(
                r['id_venta'], r['ncf'], r['cliente'], f"${r['total']:,.2f}", 
                r['fecha'].strftime("%Y-%m-%d") if hasattr(r['fecha'], 'strftime') else str(r['fecha']), 
                r['estado']
            ))

    def load_invoice_details(self):
        sel = self.inv_tree.selection()
        if not sel: return
        id_v = int(sel[0])
        data, err = self.controller.get_invoice_details(id_v)
        if err:
            messagebox.showerror("Error", err)
            return
        
        self.invoice_data = data
        self.mode_frm.pack(fill="x", padx=20, pady=10)
        self.nc_type.set("PARCIAL") # Default
        self.btn_save.configure(state="normal")
        self.on_mode_change()

    def on_mode_change(self):
        if not self.invoice_data: return
        
        mode = self.nc_type.get()
        if mode == "TOTAL":
            # Autocompletar todo
            for it in self.invoice_data['items']:
                it['qty_refund'] = it['cantidad_original']
            self.lbl_step2.configure(text="2. MODO ANULACIÓN TOTAL (Se devolverán todos los artículos)")
        else:
            # Resetear a cero para que elijan
            for it in self.invoice_data['items']:
                it['qty_refund'] = 0
            self.lbl_step2.configure(text="2. MODO DEVOLUCIÓN PARCIAL (Doble clic en 'Devolver' para editar)")
        
        self.refresh_items_grid()

    def refresh_items_grid(self):
        for i in self.items_tree.get_children(): self.items_tree.delete(i)
        total_nc = 0
        for it in self.invoice_data['items']:
            sub = it['qty_refund'] * it['precio']
            total_nc += sub
            self.items_tree.insert("", "end", iid=it['id_producto'], values=(
                it['id_producto'], it['producto'], it['cantidad_original'], 
                it['qty_refund'], f"${it['precio']:,.2f}", f"${sub:,.2f}"
            ))
        self.lbl_total_refund.configure(text=f"TOTAL A DEVOLVER: RD$ {total_nc:,.2f}")

    def on_item_double_click(self, e):
        if self.nc_type.get() == "TOTAL":
            messagebox.showinfo("Modo Total", "En este modo no puede editar cantidades individuales.")
            return
            
        sel = self.items_tree.selection()
        if not sel: return
        pid = int(sel[0])
        it = next(x for x in self.invoice_data['items'] if x['id_producto'] == pid)
        
        dialog = ctk.CTkInputDialog(text=f"¿Cuantos '{it['producto']}' desea devolver?\n(Máximo disponible: {it['cantidad_original']})", title="Editar Cantidad")
        val = dialog.get_input()
        if val and val.isdigit():
            q = int(val)
            if 0 <= q <= it['cantidad_original']:
                it['qty_refund'] = q
                self.refresh_items_grid()
            else:
                messagebox.showwarning("Invalido", "La cantidad excede el limite de la factura.")

    def process_final(self):
        reason = self.ent_reason.get().strip()
        if not reason:
            messagebox.showwarning("Atención", "Debe especificar el MOTIVO de la Nota de Crédito.")
            return
            
        total_nc = sum(x['qty_refund'] * x['precio'] for x in self.invoice_data['items'])
        if total_nc <= 0:
            messagebox.showwarning("Atención", "No se han seleccionado productos para devolver.")
            return

        is_full = (self.nc_type.get() == "TOTAL")
        msg = "¿Está seguro de ANULAR COMPLETAMENTE esta factura?" if is_full else f"¿Procesar devolución por un total de RD$ {total_nc:,.2f}?"
        
        if messagebox.askyesno("Confirmar", msg):
            payload = {
                "id_venta": self.invoice_data['id_venta'],
                "total_venta": self.invoice_data['total'],
                "usuario": self.user_data['username'],
                "motivo": reason,
                "items": self.invoice_data['items'],
                "es_total": is_full
            }
            
            ok, msg_res, id_nc = self.controller.create_credit_note(payload)
            if ok:
                messagebox.showinfo("Éxito", msg_res)
                # Generar PDF inmediatamente
                nc_info, items = self.controller.get_nc_full_details(id_nc)
                if nc_info:
                    PrintEngine.generate_credit_note(nc_info, items)
                
                self.callback() # Refrescar grid principal
                self.destroy() # Cerrar ventana
            else:
                messagebox.showerror("Error", msg_res)
