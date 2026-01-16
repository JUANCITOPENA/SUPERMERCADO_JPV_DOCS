
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.views.styles import Colors, Fonts
from src.controllers.client_controller import ClientController

class ClientsView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = ClientController()
        self.user_data = user_data
        
        # Header
        self.create_header()
        
        # Grid
        self.create_grid()
        
        # Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Gestión de Clientes", font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=20)
        
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Buscar por Nombre o RNC...", width=300)
        self.entry_search.pack(side="left", padx=20)
        self.entry_search.bind("<KeyRelease>", self.filter_data)
        
        btn_add = ctk.CTkButton(header, text="Nuevo Cliente", fg_color=Colors.SUCCESS, command=self.open_form)
        btn_add.pack(side="right", padx=10)
        
        btn_del = ctk.CTkButton(header, text="Eliminar", fg_color=Colors.DANGER, command=self.delete_client)
        btn_del.pack(side="right", padx=10)
        
        btn_edit = ctk.CTkButton(header, text="Editar", fg_color=Colors.PRIMARY, command=self.edit_client)
        btn_edit.pack(side="right", padx=10)

    def create_grid(self):
        # Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="white", 
                        foreground="black", 
                        rowheight=30, 
                        fieldbackground="white",
                        font=Fonts.BODY)
        style.map("Treeview", background=[("selected", Colors.PRIMARY)])
        
        columns = ("ID", "Nombre", "Apellido", "RNC", "Tipo", "Crédito", "Límite")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self, search=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = self.controller.get_all(search)
        for row in data:
            # row: ID, Nom, Ape, RNC, Tipo, Dir, Cred, Lim, Reg, Prov, id_reg, id_prov
            # Display: ID, Nom, Ape, RNC, Tipo, Cred(Si/No), Lim
            cred = "SI" if row[6] else "NO"
            values = (row[0], row[1], row[2], row[3], row[4], cred, f"{row[7]:,.2f}")
            self.tree.insert("", "end", values=values, tags=(str(row[0]),)) # Tag with ID for reference

        self.full_data = data # Keep full data for edit

    def filter_data(self, event):
        self.load_data(self.entry_search.get())

    def get_selected_row(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        return item['values'] # This gives display values

    def get_full_data_by_id(self, cid):
        for row in self.full_data:
            if row[0] == cid:
                return row
        return None

    def delete_client(self):
        sel = self.get_selected_row()
        if not sel: return
        cid = sel[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente ID {cid}?"):
            ok, msg = self.controller.delete(cid)
            if ok: 
                messagebox.showinfo("Éxito", msg)
                self.load_data()
            else:
                messagebox.showerror("Error", msg)

    def edit_client(self):
        sel = self.get_selected_row()
        if not sel: return
        cid = sel[0]
        full_row = self.get_full_data_by_id(cid)
        self.open_form(full_row)

    def open_form(self, data=None):
        ClientForm(self, data)

class ClientForm(ctk.CTkToplevel):
    def __init__(self, parent_view, data=None):
        super().__init__()
        self.parent_view = parent_view
        self.data = data
        self.title("Cliente" if not data else f"Editar Cliente {data[0]}")
        self.geometry("600x600")
        self.attributes("-topmost", True)
        
        self.controller = parent_view.controller
        regs, provs = self.controller.get_geo()
        self.regions = {r[1]: r[0] for r in regs} # Name: ID
        self.provinces = provs # List of tuples

        # Fields
        self.create_widgets()
        
        if data:
            self.fill_fields(data)

    def create_widgets(self):
        frm = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name
        ctk.CTkLabel(frm, text="Nombre:").grid(row=0, column=0, pady=5)
        self.ent_nom = ctk.CTkEntry(frm)
        self.ent_nom.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Last Name
        ctk.CTkLabel(frm, text="Apellido:").grid(row=1, column=0, pady=5)
        self.ent_ape = ctk.CTkEntry(frm)
        self.ent_ape.grid(row=1, column=1, pady=5, sticky="ew")
        
        # RNC
        ctk.CTkLabel(frm, text="RNC/Cédula:").grid(row=2, column=0, pady=5)
        self.ent_rnc = ctk.CTkEntry(frm)
        self.ent_rnc.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Type
        ctk.CTkLabel(frm, text="Tipo:").grid(row=3, column=0, pady=5)
        self.cmb_tipo = ctk.CTkComboBox(frm, values=["FISICA", "JURIDICA"])
        self.cmb_tipo.grid(row=3, column=1, pady=5, sticky="ew")

        # Region
        ctk.CTkLabel(frm, text="Región:").grid(row=4, column=0, pady=5)
        self.cmb_reg = ctk.CTkComboBox(frm, values=list(self.regions.keys()), command=self.filter_provinces)
        self.cmb_reg.grid(row=4, column=1, pady=5, sticky="ew")
        
        # Provincia
        ctk.CTkLabel(frm, text="Provincia:").grid(row=5, column=0, pady=5)
        self.cmb_prov = ctk.CTkComboBox(frm, values=[])
        self.cmb_prov.grid(row=5, column=1, pady=5, sticky="ew")

        # Address
        ctk.CTkLabel(frm, text="Dirección:").grid(row=6, column=0, pady=5)
        self.ent_dir = ctk.CTkEntry(frm)
        self.ent_dir.grid(row=6, column=1, pady=5, sticky="ew")
        
        # Credit
        self.chk_cred = ctk.CTkCheckBox(frm, text="Crédito Aprobado")
        self.chk_cred.grid(row=7, column=1, pady=5, sticky="w")
        
        # Limit
        ctk.CTkLabel(frm, text="Límite Crédito:").grid(row=8, column=0, pady=5)
        self.ent_lim = ctk.CTkEntry(frm)
        self.ent_lim.grid(row=8, column=1, pady=5, sticky="ew")
        
        # Buttons
        ctk.CTkButton(frm, text="Guardar", fg_color=Colors.SUCCESS, command=self.save).grid(row=9, column=1, pady=20)

    def filter_provinces(self, region_name):
        rid = self.regions[region_name]
        filtered = [p[1] for p in self.provinces if p[2] == rid]
        self.cmb_prov.configure(values=filtered)
        if filtered: self.cmb_prov.set(filtered[0])

    def fill_fields(self, row):
        # row: ID, Nom, Ape, RNC, Tipo, Dir, Cred, Lim, RegName, ProvName, id_reg, id_prov
        self.ent_nom.insert(0, row[1])
        self.ent_ape.insert(0, row[2])
        self.ent_rnc.insert(0, row[3])
        self.cmb_tipo.set(row[4])
        self.ent_dir.insert(0, row[5] or "")
        if row[6]: self.chk_cred.select()
        self.ent_lim.insert(0, str(row[7]))
        self.cmb_reg.set(row[8] or "")
        self.filter_provinces(row[8] or list(self.regions.keys())[0])
        self.cmb_prov.set(row[9] or "")

    def save(self):
        try:
            rid = self.regions[self.cmb_reg.get()]
            # Find prov id
            prov_name = self.cmb_prov.get()
            pid = next(p[0] for p in self.provinces if p[1] == prov_name)
            
            ok, msg = self.controller.save(
                self.data[0] if self.data else None,
                self.ent_nom.get(),
                self.ent_ape.get(),
                self.ent_rnc.get(),
                self.cmb_tipo.get(),
                rid,
                pid,
                self.ent_dir.get(),
                1 if self.chk_cred.get() else 0,
                float(self.ent_lim.get() or 0)
            )
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.parent_view.load_data()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
