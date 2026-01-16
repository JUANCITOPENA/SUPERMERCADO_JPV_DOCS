import customtkinter as ctk
from tkinter import ttk, messagebox
from src.views.styles import Colors, Fonts
from src.controllers.sales_controller import SalesController
from src.controllers.vendor_controller import VendorController
from src.utils.print_engine import PrintEngine

class PosView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = SalesController()
        self.ven_controller = VendorController()
        self.user_data = user_data
        self.cart = []
        self.totals = {"sub": 0, "itbis": 0, "total": 0}
        
        self.load_master_data()
        self.create_ui()

    def load_master_data(self):
        self.clients = self.controller.get_clients() # [(ID, Name, RNC, Type)]
        self.products = self.controller.get_products() # [(ID, Prod, Price, Stock)]
        self.pay_methods = self.controller.get_payment_methods()
        self.del_methods = self.controller.get_delivery_methods()
        # Ensure vendors are loaded dynamically
        self.vendors = self.ven_controller.get_all() # [(ID, Name, Sucursal...)]

    def create_ui(self):
        # 1. Header (Client & Vendor)
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL)
        header.pack(fill="x", padx=10, pady=10)
        
        # Client
        ctk.CTkLabel(header, text="Cliente:", font=Fonts.BODY).pack(side="left", padx=5)
        self.cmb_client = ctk.CTkComboBox(header, width=250, 
                                          values=[f"{c[1]} - {c[2]}" for c in self.clients],
                                          command=self.on_client_select)
        self.cmb_client.pack(side="left", padx=5)
        
        self.lbl_client_info = ctk.CTkLabel(header, text="Tipo: -", text_color="gray")
        self.lbl_client_info.pack(side="left", padx=10)

        # Vendor
        ctk.CTkLabel(header, text="Vendedor:", font=Fonts.BODY).pack(side="left", padx=5)
        # Using index 1 (Name) for display
        vendor_names = [v[1] for v in self.vendors]
        self.cmb_vendor = ctk.CTkComboBox(header, width=200, values=vendor_names)
        self.cmb_vendor.pack(side="left", padx=5)
        if vendor_names: self.cmb_vendor.set(vendor_names[0])

        # 2. Product Selection
        prod_frame = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        prod_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(prod_frame, text="Producto:").pack(side="left", padx=5)
        self.ent_search_prod = ctk.CTkEntry(prod_frame, placeholder_text="Buscar...", width=200)
        self.ent_search_prod.pack(side="left", padx=5)
        self.ent_search_prod.bind("<KeyRelease>", self.filter_products)
        
        self.cmb_product = ctk.CTkComboBox(prod_frame, width=300, values=[p[1] for p in self.products])
        self.cmb_product.pack(side="left", padx=5)
        self.cmb_product.bind("<Return>", lambda e: self.add_to_cart())
        
        ctk.CTkLabel(prod_frame, text="Cant:").pack(side="left", padx=5)
        self.ent_qty = ctk.CTkEntry(prod_frame, width=60)
        self.ent_qty.insert(0, "1")
        self.ent_qty.pack(side="left", padx=5)
        self.ent_qty.bind("<Return>", lambda e: self.add_to_cart())
        
        ctk.CTkButton(prod_frame, text="Agregar", command=self.add_to_cart, width=80).pack(side="left", padx=10)

        # 3. Cart Grid
        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("ID", "Producto", "Cant", "Precio", "ITBIS", "Total")
        self.tree = ttk.Treeview(grid_frame, columns=columns, show="headings")
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80 if c != "Producto" else 200)
        self.tree.pack(fill="both", expand=True)
        
        btn_del_item = ctk.CTkButton(self, text="Quitar Item", fg_color=Colors.DANGER, height=30, command=self.remove_item)
        btn_del_item.pack(padx=10, pady=5, anchor="e")

        # 4. Footer (Totals & Action)
        footer = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=100)
        footer.pack(fill="x", padx=10, pady=10)
        
        # Payment
        pay_frame = ctk.CTkFrame(footer, fg_color="transparent")
        pay_frame.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(pay_frame, text="Pago:").grid(row=0, column=0, padx=5)
        self.cmb_pay = ctk.CTkComboBox(pay_frame, values=[p[1] for p in self.pay_methods])
        self.cmb_pay.grid(row=0, column=1, padx=5)
        if self.pay_methods: self.cmb_pay.set(self.pay_methods[0][1])

        ctk.CTkLabel(pay_frame, text="Entrega:").grid(row=1, column=0, padx=5, pady=5)
        self.cmb_del = ctk.CTkComboBox(pay_frame, values=[d[1] for d in self.del_methods])
        self.cmb_del.grid(row=1, column=1, padx=5, pady=5)
        if self.del_methods: self.cmb_del.set(self.del_methods[0][1])

        # Totals Labels
        tot_frame = ctk.CTkFrame(footer, fg_color="transparent")
        tot_frame.pack(side="right", padx=40)
        
        self.lbl_sub = ctk.CTkLabel(tot_frame, text="Subtotal: 0.00", font=Fonts.BODY)
        self.lbl_sub.pack(anchor="e")
        self.lbl_itbis = ctk.CTkLabel(tot_frame, text="ITBIS: 0.00", font=Fonts.BODY)
        self.lbl_itbis.pack(anchor="e")
        self.lbl_total = ctk.CTkLabel(tot_frame, text="TOTAL: 0.00", font=Fonts.SUBTITLE, text_color=Colors.PRIMARY)
        self.lbl_total.pack(anchor="e")
        
        ctk.CTkButton(footer, text="FACTURAR", font=Fonts.BUTTON, height=50, width=200, 
                      fg_color=Colors.SUCCESS, command=self.process_sale).pack(side="right", padx=20)

    def filter_products(self, event):
        txt = self.ent_search_prod.get().lower()
        filtered = [p[1] for p in self.products if txt in p[1].lower()]
        self.cmb_product.configure(values=filtered)
        if filtered: self.cmb_product.set(filtered[0])

    def on_client_select(self, val):
        for c in self.clients:
            if f"{c[1]} - {c[2]}" == val:
                self.lbl_client_info.configure(text=f"Tipo: {c[3]} | RNC: {c[2]}")
                self.selected_client_id = c[0]
                break

    def add_to_cart(self):
        prod_name = self.cmb_product.get()
        qty_str = self.ent_qty.get()
        
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        prod = next((p for p in self.products if p[1] == prod_name), None)
        if not prod: return
        
        if qty > prod[3]:
            messagebox.showerror("Stock", f"Stock insuficiente. Disponible: {prod[3]}")
            return
        
        price = float(prod[2])
        itbis_unit = price * 0.18
        total = (price + itbis_unit) * qty
        
        self.cart.append({
            "id": prod[0],
            "name": prod[1],
            "qty": qty,
            "price": price,
            "itbis_unit": itbis_unit,
            "total": total
        })
        
        self.refresh_cart()
        self.ent_qty.delete(0, "end")
        self.ent_qty.insert(0, "1")

    def remove_item(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        del self.cart[idx]
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        sub = 0
        itbis = 0
        tot = 0
        
        for item in self.cart:
            row_sub = item['price'] * item['qty']
            row_itbis = item['itbis_unit'] * item['qty']
            row_tot = row_sub + row_itbis
            
            sub += row_sub
            itbis += row_itbis
            tot += row_tot
            
            self.tree.insert("", "end", values=(
                item['id'], item['name'], item['qty'], 
                f"{item['price']:,.2f}", f"{row_itbis:,.2f}", f"{row_tot:,.2f}"
            ))
            
        self.lbl_sub.configure(text=f"Subtotal: {sub:,.2f}")
        self.lbl_itbis.configure(text=f"ITBIS: {itbis:,.2f}")
        self.lbl_total.configure(text=f"TOTAL: {tot:,.2f}")
        
        self.totals = {"sub": sub, "itbis": itbis, "total": tot}

    def process_sale(self):
        if not self.cart:
            messagebox.showwarning("Vacío", "El carrito está vacío")
            return
        
        if not hasattr(self, 'selected_client_id'):
            val = self.cmb_client.get()
            match = next((c for c in self.clients if f"{c[1]} - {c[2]}" == val), None)
            if match: self.selected_client_id = match[0]
            else:
                messagebox.showerror("Error", "Seleccione un cliente válido")
                return

        # Fix Vendor ID
        v_name = self.cmb_vendor.get()
        # Ensure we pick the ID (index 0) where name (index 1) matches
        vid = next((v[0] for v in self.vendors if v[1] == v_name), 1)
        
        p_name = self.cmb_pay.get()
        pid = next((p[0] for p in self.pay_methods if p[1] == p_name), 1)

        d_name = self.cmb_del.get()
        did = next((d[0] for d in self.del_methods if d[1] == d_name), 1)

        ok, res = self.controller.process_full_sale(
            self.selected_client_id, vid, self.cart, pid, did, 
            self.totals['total'], self.totals['sub'], self.totals['itbis']
        )
        
        if ok:
            messagebox.showinfo("Éxito", f"Venta Facturada: {res['ncf']}")
            
            c_obj = next(c for c in self.clients if c[0] == self.selected_client_id)
            sale_data = {
                "id": res['id'],
                "ncf": res['ncf'],
                "ncf_type": res['ncf_type'],
                "payment_cond": res['payment_cond'],
                "client_name": c_obj[1],
                "client_rnc": c_obj[2],
                "subtotal": self.totals['sub'],
                "itbis": self.totals['itbis'],
                "total": self.totals['total']
            }
            try:
                PrintEngine.generate_invoice(sale_data, self.cart)
            except Exception as e:
                messagebox.showerror("Error Impresión", str(e))
                
            self.cart = []
            self.refresh_cart()
            self.products = self.controller.get_products() 
        else:
            messagebox.showerror("Error", res)
