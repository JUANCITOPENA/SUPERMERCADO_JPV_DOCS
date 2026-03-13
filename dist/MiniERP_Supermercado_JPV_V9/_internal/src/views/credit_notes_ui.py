import customtkinter as ctk
from tkinter import ttk, messagebox
from src.controllers.credit_note_controller import CreditNoteController
from src.views.styles import Colors, Fonts

class CreditNoteWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.controller = CreditNoteController()
        
        self.title("⚙️ Módulo Profesional de Notas de Crédito - V9")
        self.geometry("1150x780")
        self.configure(fg_color=Colors.BACKGROUND)
        self.after(200, self.lift)
        
        self.current_invoice = None
        self.invoice_items = []

        self.init_ui()

    def init_ui(self):
        # --- SIDEBAR: SELECCIÓN ---
        side = ctk.CTkFrame(self, width=300, fg_color=Colors.PANEL)
        side.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(side, text="📍 SELECCIÓN DE FACTURA", font=Fonts.SUBTITLE).pack(pady=10)
        
        # Búsqueda manual
        search_frm = ctk.CTkFrame(side, fg_color="transparent")
        search_frm.pack(fill="x", padx=10)
        self.ent_search = ctk.CTkEntry(search_frm, placeholder_text="Escriba NCF aquí...", width=180)
        self.ent_search.pack(side="left", padx=2)
        ctk.CTkButton(search_frm, text="BUSCAR", width=70, command=self.btn_search_click).pack(side="left")

        ctk.CTkLabel(side, text="Recientes (Doble clic p/cargar):", font=Fonts.LABEL).pack(pady=(20, 5), padx=10, anchor="w")
        
        cols = ("NCF", "Total", "Estado")
        self.tree_list = ttk.Treeview(side, columns=cols, show="headings", height=20)
        self.tree_list.heading("NCF", text="NCF")
        self.tree_list.heading("Total", text="Total")
        self.tree_list.heading("Estado", text="Est.")
        self.tree_list.column("NCF", width=110)
        self.tree_list.column("Total", width=80)
        self.tree_list.column("Estado", width=60)
        self.tree_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_list.bind("<Double-1>", self.on_list_double_click)

        # --- CONTENIDO: PROCESAMIENTO ---
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Info de Factura
        self.info_box = ctk.CTkFrame(content, fg_color=Colors.PRIMARY, height=100)
        self.info_box.pack(fill="x", pady=(0, 10))
        self.lbl_head = ctk.CTkLabel(self.info_box, text="PASO 1: SELECCIONE UNA FACTURA DE LA LISTA O BUSQUE POR NCF", 
                                    font=Fonts.SUBTITLE, text_color="white")
        self.lbl_head.pack(pady=20)

        # Tabla de Items
        ctk.CTkLabel(content, text="📋 ARTÍCULOS ENCONTRADOS (Haga doble clic en la cantidad para devolver parcial):", 
                    font=Fonts.LABEL_BOLD).pack(anchor="w")
        
        cols_it = ("ID", "Producto", "Cant. Original", "A Devolver", "Precio", "Subtotal Dev.")
        self.tree_items = ttk.Treeview(content, columns=cols_it, show="headings", height=12)
        for c in cols_it: 
            self.tree_items.heading(c, text=c)
            self.tree_items.column(c, width=100)
        self.tree_items.pack(fill="x", pady=5)
        self.tree_items.bind("<Double-1>", self.on_item_double_click)

        # Acciones
        ctrl_frm = ctk.CTkFrame(content, fg_color=Colors.PANEL)
        ctrl_frm.pack(fill="both", expand=True, pady=10)
        
        # Botones Rápidos
        btn_box = ctk.CTkFrame(ctrl_frm, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_box, text="❌ ANULAR FACTURA COMPLETA", fg_color=Colors.DANGER, 
                      command=self.action_full_refund, height=40).pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(btn_box, text="🧹 LIMPIAR SELECCIÓN", fg_color="gray", 
                      command=self.clear_form, height=40).pack(side="left", padx=5, expand=True, fill="x")

        # Comentario
        ctk.CTkLabel(ctrl_frm, text="Motivo del Crédito:", font=Fonts.LABEL).pack(anchor="w", padx=25)
        self.ent_comment = ctk.CTkEntry(ctrl_frm, width=600, placeholder_text="Ej: Error en precio / Devolución de mercancía dañada")
        self.ent_comment.pack(pady=5, padx=25)

        # Resumen Final
        self.lbl_total = ctk.CTkLabel(ctrl_frm, text="TOTAL NOTA CRÉDITO: $0.00", 
                                     font=("Arial", 24, "bold"), text_color=Colors.SUCCESS)
        self.lbl_total.pack(pady=20)

        self.btn_save = ctk.CTkButton(ctrl_frm, text="💾 GENERAR Y APLICAR NOTA DE CRÉDITO (B04)", 
                                     fg_color=Colors.SUCCESS, height=60, font=Fonts.TITLE, 
                                     command=self.process_final, state="disabled")
        self.btn_save.pack(pady=10, padx=50, fill="x")

        self.refresh_list()

    def refresh_list(self):
        for i in self.tree_list.get_children(): self.tree_list.delete(i)
        data = self.controller.get_recent_invoices()
        for r in data:
            self.tree_list.insert("", "end", values=(r['ncf'], f"${r['total']:,.2f}", r['estado']))

    def on_list_double_click(self, e):
        sel = self.tree_list.selection()
        if sel:
            ncf = self.tree_list.item(sel[0])['values'][0]
            self.load_invoice(ncf)

    def btn_search_click(self):
        self.load_invoice(self.ent_search.get())

    def load_invoice(self, ncf):
        data, err = self.controller.get_invoice_details(ncf)
        if err:
            messagebox.showerror("Búsqueda Fallida", err)
            return
        
        self.current_invoice = data
        self.invoice_items = data['items']
        self.lbl_head.configure(text=f"✅ CARGADA: {data['ncf']} | Cliente: {data['estado']} | Total: ${data['total']:,.2f}")
        self.update_items_table()
        self.btn_save.configure(state="normal")
        self.calculate()

    def update_items_table(self):
        for i in self.tree_items.get_children(): self.tree_items.delete(i)
        for it in self.invoice_items:
            sub = it['qty_refund'] * it['precio']
            self.tree_items.insert("", "end", iid=it['id_producto'], values=(
                it['id_producto'], it['producto'], it['cantidad_original'], 
                it['qty_refund'], f"${it['precio']:.2f}", f"${sub:.2f}"
            ))

    def on_item_double_click(self, e):
        sel = self.tree_items.selection()
        if not sel: return
        item_id = int(sel[0])
        it = next(x for x in self.invoice_items if x['id_producto'] == item_id)
        
        dialog = ctk.CTkInputDialog(text=f"Unidades a devolver de {it['producto']}\n(Máximo disponible: {it['cantidad_original']})", title="Cant. Devolución")
        val = dialog.get_input()
        if val and val.isdigit():
            q = int(val)
            if 0 <= q <= it['cantidad_original']:
                it['qty_refund'] = q
                self.update_items_table()
                self.calculate()
            else: messagebox.showwarning("Error", "Cantidad excede el original")

    def action_full_refund(self):
        if not self.current_invoice: return
        if messagebox.askyesno("Confirmar", "¿Desea anular la factura COMPLETA?"):
            for it in self.invoice_items:
                it['qty_refund'] = it['cantidad_original']
            self.update_items_table()
            self.calculate()

    def calculate(self):
        t = sum(x['qty_refund'] * x['precio'] for x in self.invoice_items)
        self.lbl_total.configure(text=f"TOTAL NOTA CRÉDITO: ${t:,.2f}")
        return t

    def process_final(self):
        total = self.calculate()
        if total <= 0:
            messagebox.showwarning("Aviso", "Seleccione al menos un artículo para devolver.")
            return
        
        if not messagebox.askyesno("Confirmar", f"Se generará una Nota de Crédito por ${total:,.2f}.\nEl inventario se actualizará. ¿Continuar?"):
            return

        payload = {
            "ncf_afectado": self.current_invoice['ncf'],
            "tipo": "ANULACION" if total >= self.current_invoice['total'] else "DEVOLUCION",
            "usuario": self.user_data['username'],
            "comentario": self.ent_comment.get(),
            "items": [x for x in self.invoice_items if x['qty_refund'] > 0]
        }

        # Convertir a formato esperado por controlador
        data_to_send = {
            "ncf_afectado": payload['ncf_afectado'],
            "tipo": payload['tipo'],
            "usuario": payload['usuario'],
            "comentario": payload['comentario'],
            "items": [{"id_producto": x['id_producto'], "cantidad": x['qty_refund'], "precio": x['precio']} for x in payload['items']]
        }

        ok, msg = self.controller.create_credit_note(data_to_send)
        if ok:
            messagebox.showinfo("Proceso Exitoso", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", msg)

    def clear_form(self):
        self.current_invoice = None
        self.invoice_items = []
        self.ent_search.delete(0, "end")
        self.ent_comment.delete(0, "end")
        self.lbl_head.configure(text="PASO 1: SELECCIONE UNA FACTURA DE LA LISTA O BUSQUE POR NCF")
        self.update_items_table()
        self.btn_save.configure(state="disabled")
        self.calculate()
