
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.views.styles import Colors, Fonts
from src.controllers.aux_controller import AuxController
from src.utils.print_engine import PrintEngine

class BaseMasterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, title, columns):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        self.controller = controller
        self.title_text = title
        self.columns = columns # list of (header, width)
        
        self.create_header()
        self.create_grid()
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Colors.PANEL, height=50)
        header.pack(fill="x", padx=5, pady=5)
        
        lbl = ctk.CTkLabel(header, text=self.title_text, font=Fonts.SUBTITLE, text_color=Colors.TEXT)
        lbl.pack(side="left", padx=10)
        
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Buscar...", width=200)
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<KeyRelease>", self.filter_data)
        
        btn_add = ctk.CTkButton(header, text="Nuevo", width=80, fg_color=Colors.SUCCESS, command=self.open_form)
        btn_add.pack(side="right", padx=5)
        
        btn_del = ctk.CTkButton(header, text="Eliminar", width=80, fg_color=Colors.DANGER, command=self.delete_item)
        btn_del.pack(side="right", padx=5)
        
        btn_edit = ctk.CTkButton(header, text="Editar", width=80, fg_color=Colors.PRIMARY, command=self.edit_item)
        btn_edit.pack(side="right", padx=5)
        
        btn_rep = ctk.CTkButton(header, text="PDF", width=60, fg_color="gray", command=self.generate_report)
        btn_rep.pack(side="right", padx=5)

    def create_grid(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=25, font=Fonts.BODY)
        style.map("Treeview", background=[("selected", Colors.PRIMARY)])
        
        cols = [c[0] for c in self.columns]
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        for c_name, c_width in self.columns:
            self.tree.heading(c_name, text=c_name)
            self.tree.column(c_name, width=c_width)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def get_selected_row(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        return item['values'] 
    
    def get_full_data_by_id(self, pk):
        for row in self.full_data:
            if str(row[0]) == str(pk):
                return row
        return None

    def generate_report(self):
        if not hasattr(self, 'full_data') or not self.full_data:
            return
        
        headers = [c[0] for c in self.columns]
        # full_data might have more columns than headers (e.g. FK IDs). We need to filter/format.
        # But wait, BaseMasterFrame doesn't know which columns are which in full_data vs view.
        # Simple solution: Use the data displayed in the treeview (self.tree.get_children())
        
        report_data = []
        for item_id in self.tree.get_children():
            row = self.tree.item(item_id)['values']
            report_data.append(list(row))
            
        filename = f"Reporte_{self.title_text.replace(' ', '_')}.pdf"
        PrintEngine.generate_simple_list_pdf(f"Reporte de {self.title_text}", report_data, headers, filename)

    def load_data(self, search=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = self.fetch_data(search) # Abstract
        self.full_data = data
        
        for row in data:
            self.insert_row(row) # Abstract

    def filter_data(self, event):
        self.load_data(self.entry_search.get())

    # Abstract methods to be overridden
    def fetch_data(self, search): pass
    def insert_row(self, row): pass
    def delete_item(self): pass
    def open_form(self, data=None): pass
    def edit_item(self):
        sel = self.get_selected_row()
        if not sel: return
        pk = sel[0]
        full_row = self.get_full_data_by_id(pk)
        self.open_form(full_row)

# --- IMPLEMENTATIONS ---

class RegionFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Regiones", [("ID", 50), ("Región", 300)])
    
    def fetch_data(self, search): return self.controller.get_regions(search)
    
    def insert_row(self, row):
        self.tree.insert("", "end", values=(row[0], row[1]))
        
    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Región?"):
            ok, msg = self.controller.delete_region(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        SimpleForm(self, "Región", data, self.save_action)

    def save_action(self, form, data_id):
        return self.controller.save_region(data_id, form.ent_name.get())


class GeneroFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Géneros", [("ID", 50), ("Género", 300)])
    
    def fetch_data(self, search): return self.controller.get_generos(search)
    
    def insert_row(self, row):
        self.tree.insert("", "end", values=(row[0], row[1]))

    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Género?"):
            ok, msg = self.controller.delete_genero(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        SimpleForm(self, "Género", data, self.save_action)

    def save_action(self, form, data_id):
        return self.controller.save_genero(data_id, form.ent_name.get())


class MetodoPagoFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Métodos de Pago", [("ID", 50), ("Método", 300)])
    
    def fetch_data(self, search): return self.controller.get_metodos_pago(search)
    
    def insert_row(self, row):
        self.tree.insert("", "end", values=(row[0], row[1]))

    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Método?"):
            ok, msg = self.controller.delete_metodo_pago(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        SimpleForm(self, "Método Pago", data, self.save_action)

    def save_action(self, form, data_id):
        return self.controller.save_metodo_pago(data_id, form.ent_name.get())


class CondicionFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Condiciones Pago", [("ID", 50), ("Nombre", 250), ("Crédito", 80)])
    
    def fetch_data(self, search): return self.controller.get_condiciones(search)
    
    def insert_row(self, row):
        # row: ID, Name, EsCredito
        cred = "SI" if row[2] else "NO"
        self.tree.insert("", "end", values=(row[0], row[1], cred))

    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Condición?"):
            ok, msg = self.controller.delete_condicion(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        BooleanForm(self, "Condición Pago", "Es Crédito", data, self.save_action)

    def save_action(self, form, data_id):
        return self.controller.save_condicion(data_id, form.ent_name.get(), 1 if form.chk_bool.get() else 0)


class MetodoEntregaFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Métodos Entrega", [("ID", 50), ("Tipo", 250), ("Online", 80)])
    
    def fetch_data(self, search): return self.controller.get_metodos_entrega(search)
    
    def insert_row(self, row):
        # row: ID, Name, EsOnline
        online = "SI" if row[2] else "NO"
        self.tree.insert("", "end", values=(row[0], row[1], online))

    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Método?"):
            ok, msg = self.controller.delete_metodo_entrega(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        BooleanForm(self, "Método Entrega", "Es Online", data, self.save_action)

    def save_action(self, form, data_id):
        return self.controller.save_metodo_entrega(data_id, form.ent_name.get(), 1 if form.chk_bool.get() else 0)


class ProvinciasFrame(BaseMasterFrame):
    def __init__(self, parent):
        super().__init__(parent, AuxController(), "Provincias", [("ID", 50), ("Nombre", 200), ("Región", 150)])
    
    def fetch_data(self, search): return self.controller.get_provincias(search)
    
    def insert_row(self, row):
        # row: ID, Name, RegName, RegID
        self.tree.insert("", "end", values=(row[0], row[1], row[2]))

    def delete_item(self):
        sel = self.get_selected_row()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar Provincia?"):
            ok, msg = self.controller.delete_provincia(sel[0])
            if ok: self.load_data(); messagebox.showinfo("Info", msg)
            else: messagebox.showerror("Error", msg)

    def open_form(self, data=None):
        ProvinciaForm(self, data)


# --- FORMS ---

class SimpleForm(ctk.CTkToplevel):
    def __init__(self, parent_view, entity_name, data, save_callback):
        super().__init__()
        self.parent_view = parent_view
        self.save_callback = save_callback
        self.data = data
        self.title(f"{entity_name} - {'Editar' if data else 'Nuevo'}")
        self.geometry("400x200")
        
        frm = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frm, text="Nombre/Descripción:").pack(pady=5)
        self.ent_name = ctk.CTkEntry(frm)
        self.ent_name.pack(fill="x", padx=20, pady=5)
        
        if data: self.ent_name.insert(0, data[1])
        
        ctk.CTkButton(frm, text="Guardar", fg_color=Colors.SUCCESS, command=self.save).pack(pady=20)

    def save(self):
        ok, msg = self.save_callback(self, self.data[0] if self.data else None)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.parent_view.load_data()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class BooleanForm(ctk.CTkToplevel):
    def __init__(self, parent_view, entity_name, bool_label, data, save_callback):
        super().__init__()
        self.parent_view = parent_view
        self.save_callback = save_callback
        self.data = data
        self.title(f"{entity_name} - {'Editar' if data else 'Nuevo'}")
        self.geometry("400x250")
        
        frm = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frm, text="Nombre/Descripción:").pack(pady=5)
        self.ent_name = ctk.CTkEntry(frm)
        self.ent_name.pack(fill="x", padx=20, pady=5)
        
        self.chk_bool = ctk.CTkCheckBox(frm, text=bool_label)
        self.chk_bool.pack(pady=10)
        
        if data: 
            self.ent_name.insert(0, data[1])
            if data[2]: self.chk_bool.select()
        
        ctk.CTkButton(frm, text="Guardar", fg_color=Colors.SUCCESS, command=self.save).pack(pady=20)

    def save(self):
        ok, msg = self.save_callback(self, self.data[0] if self.data else None)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.parent_view.load_data()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class ProvinciaForm(ctk.CTkToplevel):
    def __init__(self, parent_view, data):
        super().__init__()
        self.parent_view = parent_view
        self.data = data
        self.controller = parent_view.controller
        self.title("Provincia")
        self.geometry("400x300")
        
        # Fetch regions
        self.regions_raw = self.controller.get_regions()
        self.regions_map = {r[1]: r[0] for r in self.regions_raw} # Name -> ID
        
        frm = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frm, text="Provincia:").pack(pady=5)
        self.ent_name = ctk.CTkEntry(frm)
        self.ent_name.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(frm, text="Región:").pack(pady=5)
        self.cmb_reg = ctk.CTkComboBox(frm, values=list(self.regions_map.keys()))
        self.cmb_reg.pack(fill="x", padx=20, pady=5)
        
        if data:
            self.ent_name.insert(0, data[1])
            self.cmb_reg.set(data[2]) # data[2] is Region Name in the view tuple
        
        ctk.CTkButton(frm, text="Guardar", fg_color=Colors.SUCCESS, command=self.save).pack(pady=20)

    def save(self):
        try:
            reg_name = self.cmb_reg.get()
            reg_id = self.regions_map.get(reg_name)
            if not reg_id: raise Exception("Seleccione una región válida")
            
            ok, msg = self.controller.save_provincia(
                self.data[0] if self.data else None,
                self.ent_name.get(),
                reg_id
            )
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.parent_view.load_data()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))


class AuxMastersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BACKGROUND)
        
        # TabView
        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add Tabs
        self.tabview.add("🌍 Regiones")
        self.tabview.add("📍 Provincias")
        self.tabview.add("⚧ Género")
        self.tabview.add("💳 Cond. Pago")
        self.tabview.add("💵 Mét. Pago")
        self.tabview.add("🚚 Mét. Entrega")
        
        # Instantiate Frames
        RegionFrame(self.tabview.tab("🌍 Regiones")).pack(fill="both", expand=True)
        ProvinciasFrame(self.tabview.tab("📍 Provincias")).pack(fill="both", expand=True)
        GeneroFrame(self.tabview.tab("⚧ Género")).pack(fill="both", expand=True)
        CondicionFrame(self.tabview.tab("💳 Cond. Pago")).pack(fill="both", expand=True)
        MetodoPagoFrame(self.tabview.tab("💵 Mét. Pago")).pack(fill="both", expand=True)
        MetodoEntregaFrame(self.tabview.tab("🚚 Mét. Entrega")).pack(fill="both", expand=True)
