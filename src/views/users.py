
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.views.styles import Colors, Fonts
from src.controllers.user_controller import UserController

class UsersView(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = UserController()
        self.user_data = user_data # Current logged user
        
        self.create_header()
        self.create_grid()
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Gestión de Usuarios", font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=20)
        
        btn_add = ctk.CTkButton(header, text="Nuevo Usuario", fg_color=Colors.SUCCESS, command=self.open_form)
        btn_add.pack(side="right", padx=10)
        
        btn_del = ctk.CTkButton(header, text="Eliminar", fg_color=Colors.DANGER, command=self.delete_user)
        btn_del.pack(side="right", padx=10)
        
        btn_edit = ctk.CTkButton(header, text="Editar", fg_color=Colors.PRIMARY, command=self.edit_user)
        btn_edit.pack(side="right", padx=10)

    def create_grid(self):
        self.tree = ttk.Treeview(self, columns=("ID", "Usuario", "Rol", "Región"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50)
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Rol", text="Rol")
        self.tree.heading("Región", text="ID Región")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = self.controller.get_all()
        for row in data:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))

    def delete_user(self):
        sel = self.tree.selection()
        if not sel: return
        uid = int(self.tree.item(sel[0])['values'][0])
        if messagebox.askyesno("Confirmar", "¿Eliminar usuario?"):
            ok, msg = self.controller.delete(uid)
            if ok: self.load_data()
            else: messagebox.showerror("Error", msg)

    def edit_user(self):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.open_form(vals)

    def open_form(self, data=None):
        UserForm(self, data)

class UserForm(ctk.CTkToplevel):
    def __init__(self, parent, data=None):
        super().__init__()
        self.parent = parent
        self.data = data
        self.controller = parent.controller
        self.title("Usuario")
        self.geometry("400x400")
        
        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frm, text="Usuario:").pack(pady=5)
        self.ent_user = ctk.CTkEntry(frm)
        self.ent_user.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frm, text="Contraseña (Dejar vacío si no cambia):").pack(pady=5)
        self.ent_pass = ctk.CTkEntry(frm, show="*")
        self.ent_pass.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frm, text="Rol:").pack(pady=5)
        self.cmb_rol = ctk.CTkComboBox(frm, values=["admin", "supervisor", "vendedor"])
        self.cmb_rol.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frm, text="ID Región (Opcional):").pack(pady=5)
        self.ent_reg = ctk.CTkEntry(frm)
        self.ent_reg.pack(pady=5, fill="x")
        
        if data:
            self.ent_user.insert(0, data[1])
            self.cmb_rol.set(data[2])
            self.ent_reg.insert(0, str(data[3]) if data[3] else "")
            
        ctk.CTkButton(frm, text="Guardar", command=self.save, fg_color=Colors.SUCCESS).pack(pady=20)

    def save(self):
        uid = self.data[0] if self.data else None
        u = self.ent_user.get()
        p = self.ent_pass.get()
        r = self.cmb_rol.get()
        reg = self.ent_reg.get() or None
        
        ok, msg = self.controller.save(uid, u, p, r, reg)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
