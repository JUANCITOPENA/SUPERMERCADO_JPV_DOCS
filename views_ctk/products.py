
import customtkinter as ctk
from tkinter import ttk, messagebox
from views_ctk.styles import Colors, Fonts
from controllers.products_controller import ProductController
from utils.image_loader import ImageLoader
import threading

class ProductsView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = ProductController()
        self.user_data = user_data
        
        self.create_header()
        self.create_grid()
        self.create_detail_panel()
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Gestión de Productos", font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=20)
        
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Buscar...", width=300)
        self.entry_search.pack(side="left", padx=20)
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_data(self.entry_search.get()))
        
        btn_add = ctk.CTkButton(header, text="Nuevo Producto", fg_color=Colors.SUCCESS, command=self.open_form)
        btn_add.pack(side="right", padx=10)
        
        btn_del = ctk.CTkButton(header, text="Eliminar", fg_color=Colors.DANGER, command=self.delete_product)
        btn_del.pack(side="right", padx=10)
        
        btn_edit = ctk.CTkButton(header, text="Editar", fg_color=Colors.PRIMARY, command=self.edit_product)
        btn_edit.pack(side="right", padx=10)

    def create_grid(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.grid_frame.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Producto", "Stock", "Precio Venta", "Costo")
        self.tree = ttk.Treeview(self.grid_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def create_detail_panel(self):
        self.preview_frame = ctk.CTkFrame(self, width=200, fg_color=Colors.PANEL)
        self.preview_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(self.preview_frame, text="Vista Previa", font=Fonts.BUTTON).pack(pady=10)
        self.img_label = ctk.CTkLabel(self.preview_frame, text="Sin Imagen", width=150, height=150)
        self.img_label.pack(pady=10, padx=10)

    def load_data(self, search=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.full_data = self.controller.get_all(search)
        for row in self.full_data:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:,.2f}", f"{row[5]:,.2f}"), tags=(str(row[0]),))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item_vals = self.tree.item(sel[0])['values']
        pid = item_vals[0]
        
        row = next((r for r in self.full_data if r[0] == pid), None)
        if row and row[4]:
            self.load_image_async(row[4])
        else:
            self.img_label.configure(image=None, text="Sin Imagen")

    def load_image_async(self, url):
        # 1. Define UI update callback (Main Thread)
        def update_ui(pil_image):
            if not self.winfo_exists(): return # Safety check if widget destroyed
            if pil_image:
                # Convert PIL to CTkImage HERE in Main Thread
                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
                self.img_label.configure(image=ctk_img, text="")
            else:
                self.img_label.configure(image=None, text="Error carga")

        # 2. Define Background Task
        def task():
            # Heavy lifting (Download) happens here
            img = ImageLoader.load_image_data(url)
            # Schedule update on Main Thread
            self.after(0, update_ui, img)

        # 3. Start Thread
        threading.Thread(target=task, daemon=True).start()

    def delete_product(self):
        sel = self.tree.selection()
        if not sel: return
        pid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            ok, msg = self.controller.delete(pid)
            if ok: self.load_data()
            else: messagebox.showerror("Error", msg)

    def edit_product(self):
        sel = self.tree.selection()
        if not sel: return
        pid = self.tree.item(sel[0])['values'][0]
        row = next((r for r in self.full_data if r[0] == pid), None)
        self.open_form(row)

    def open_form(self, data=None):
        ProductForm(self, data)

class ProductForm(ctk.CTkToplevel):
    def __init__(self, parent_view, data=None):
        super().__init__()
        self.parent_view = parent_view
        self.data = data
        self.controller = parent_view.controller
        self.title("Producto")
        self.geometry("500x600")
        self.attributes("-topmost", True)
        self.create_widgets()
        if data: self.fill_fields(data)

    def create_widgets(self):
        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.entries = {}
        labels = [("ID", "id"), ("Producto", "nom"), ("Stock", "stock"), ("Precio Compra", "pc"), ("Precio Venta", "pv"), ("URL Foto", "url")]
        
        for i, (lbl, key) in enumerate(labels):
            ctk.CTkLabel(frm, text=lbl).grid(row=i, column=0, pady=5)
            ent = ctk.CTkEntry(frm, width=250)
            if key == "id": ent.configure(state="normal") 
            ent.grid(row=i, column=1, pady=5)
            self.entries[key] = ent
            
        btn = ctk.CTkButton(frm, text="Guardar", command=self.save, fg_color=Colors.SUCCESS)
        btn.grid(row=len(labels), column=1, pady=20)

    def fill_fields(self, row):
        self.entries['id'].insert(0, row[0])
        self.entries['id'].configure(state="disabled")
        self.entries['nom'].insert(0, row[1])
        self.entries['stock'].insert(0, str(row[2]))
        self.entries['pv'].insert(0, str(row[3]))
        self.entries['url'].insert(0, row[4])
        self.entries['pc'].insert(0, str(row[5]))

    def save(self):
        try:
            id_p = int(self.entries['id'].get()) if self.entries['id'].get() else None
            nom = self.entries['nom'].get()
            stock = int(self.entries['stock'].get())
            pc = float(self.entries['pc'].get())
            pv = float(self.entries['pv'].get())
            url = self.entries['url'].get()
            
            ok, msg = self.controller.save(id_p, nom, stock, pc, pv, url)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.parent_view.load_data()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
