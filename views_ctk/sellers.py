import customtkinter as ctk
from tkinter import ttk, messagebox
from views_ctk.styles import Colors, Fonts
from controllers.vendor_controller import VendorController
from utils.image_loader import ImageLoader
import threading

class SellersView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = VendorController()
        self.user_data = user_data
        
        self.create_header()
        self.create_grid()
        self.create_detail_panel()
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Gestión de Vendedores", font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=20)
        
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Buscar...", width=300)
        self.entry_search.pack(side="left", padx=20)
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_data(self.entry_search.get()))
        
        btn_add = ctk.CTkButton(header, text="Nuevo Vendedor", fg_color=Colors.SUCCESS, command=self.open_form)
        btn_add.pack(side="right", padx=10)
        
        btn_del = ctk.CTkButton(header, text="Eliminar", fg_color=Colors.DANGER, command=self.delete_seller)
        btn_del.pack(side="right", padx=10)
        
        btn_edit = ctk.CTkButton(header, text="Editar", fg_color=Colors.PRIMARY, command=self.edit_seller)
        btn_edit.pack(side="right", padx=10)

    def create_grid(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.grid_frame.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Nombre", "Sucursal", "Provincia")
        self.tree = ttk.Treeview(self.grid_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def create_detail_panel(self):
        self.preview_frame = ctk.CTkFrame(self, width=200, fg_color=Colors.PANEL)
        self.preview_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(self.preview_frame, text="Foto", font=Fonts.BUTTON).pack(pady=10)
        self.img_label = ctk.CTkLabel(self.preview_frame, text="Sin Foto", width=150, height=150)
        self.img_label.pack(pady=10, padx=10)

    def load_data(self, search=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.full_data = self.controller.get_all(search)
        for row in self.full_data:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]), tags=(str(row[0]),))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item_vals = self.tree.item(sel[0])['values']
        vid = item_vals[0]
        
        row = next((r for r in self.full_data if r[0] == vid), None)
        if row and row[4]:
            self.load_image_async(row[4])
        else:
            self.img_label.configure(image=None, text="Sin Foto")

    def load_image_async(self, url):
        # 1. Update Callback (Main Thread)
        def update_ui(pil_image):
            if not self.winfo_exists(): return
            if pil_image:
                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
                self.img_label.configure(image=ctk_img, text="")
            else:
                self.img_label.configure(image=None, text="Error carga")
        
        # 2. Task (Thread)
        def task():
            img = ImageLoader.load_image_data(url)
            self.after(0, update_ui, img)
            
        threading.Thread(target=task, daemon=True).start()

    def delete_seller(self):
        sel = self.tree.selection()
        if not sel: return
        vid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este vendedor?"):
            ok, msg = self.controller.delete(vid)
            if ok: self.load_data()
            else: messagebox.showerror("Error", msg)

    def edit_seller(self):
        sel = self.tree.selection()
        if not sel: return
        vid = self.tree.item(sel[0])['values'][0]
        row = next((r for r in self.full_data if r[0] == vid), None)
        self.open_form(row)

    def open_form(self, data=None):
        SellerForm(self, data)

class SellerForm(ctk.CTkToplevel):
    def __init__(self, parent_view, data=None):
        super().__init__()
        self.parent_view = parent_view
        self.data = data
        self.controller = parent_view.controller
        self.title("Vendedor")
        self.geometry("500x500")
        self.attributes("-topmost", True)
        
        self.provinces = self.controller.get_geo()
        self.create_widgets()
        if data: self.fill_fields(data)

    def create_widgets(self):
        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frm, text="ID (Auto)").grid(row=0, column=0, pady=5)
        self.ent_id = ctk.CTkEntry(frm, width=250)
        if self.data: self.ent_id.configure(state="normal")
        self.ent_id.grid(row=0, column=1, pady=5)
        
        ctk.CTkLabel(frm, text="Nombre").grid(row=1, column=0, pady=5)
        self.ent_nom = ctk.CTkEntry(frm, width=250)
        self.ent_nom.grid(row=1, column=1, pady=5)

        ctk.CTkLabel(frm, text="Sucursal").grid(row=2, column=0, pady=5)
        self.ent_suc = ctk.CTkEntry(frm, width=250)
        self.ent_suc.grid(row=2, column=1, pady=5)

        ctk.CTkLabel(frm, text="Provincia").grid(row=3, column=0, pady=5)
        self.cmb_prov = ctk.CTkComboBox(frm, values=[p[1] for p in self.provinces], width=250)
        self.cmb_prov.grid(row=3, column=1, pady=5)

        ctk.CTkLabel(frm, text="Género").grid(row=4, column=0, pady=5)
        self.cmb_gen = ctk.CTkComboBox(frm, values=["Masculino", "Femenino"], width=250)
        self.cmb_gen.grid(row=4, column=1, pady=5)

        ctk.CTkLabel(frm, text="URL Foto").grid(row=5, column=0, pady=5)
        self.ent_url = ctk.CTkEntry(frm, width=250)
        self.ent_url.grid(row=5, column=1, pady=5)
            
        btn = ctk.CTkButton(frm, text="Guardar", command=self.save, fg_color=Colors.SUCCESS)
        btn.grid(row=6, column=1, pady=20)

    def fill_fields(self, row):
        self.ent_id.insert(0, row[0])
        self.ent_id.configure(state="disabled")
        self.ent_nom.insert(0, row[1])
        self.ent_suc.insert(0, row[2] or "")
        self.cmb_prov.set(row[3] or "")
        
        gen_map = {1: "Masculino", 2: "Femenino"}
        self.cmb_gen.set(gen_map.get(row[6], "Masculino"))
        self.ent_url.insert(0, row[4])

    def save(self):
        try:
            id_v = int(self.ent_id.get()) if self.ent_id.get() else None
            nom = self.ent_nom.get()
            suc = self.ent_suc.get()
            prov_name = self.cmb_prov.get()
            pid = next((p[0] for p in self.provinces if p[1] == prov_name), 1)
            gen = 1 if self.cmb_gen.get() == "Masculino" else 2
            url = self.ent_url.get()
            
            ok, msg = self.controller.save(id_v, nom, suc, pid, gen, url)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.parent_view.load_data()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")