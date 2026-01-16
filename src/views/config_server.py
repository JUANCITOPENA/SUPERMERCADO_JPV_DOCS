import customtkinter as ctk
from src.views.styles import Colors, Fonts
from src.config.settings import ConfigManager
from tkinter import messagebox
import re

class ConfigServerView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurar Servidor")
        self.geometry("400x300")
        self.resizable(False, False)
        self.attributes("-topmost", True) # Siempre encima
        
        # Center window
        self.center_window()
        
        self.configure(fg_color=Colors.BACKGROUND)
        self.create_widgets()
        self.load_current()

    def center_window(self):
        w, h = 400, 300
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def create_widgets(self):
        # Header
        ctk.CTkLabel(self, text="Conexión a Base de Datos", font=Fonts.SUBTITLE, text_color=Colors.PRIMARY).pack(pady=(20, 10))
        
        ctk.CTkLabel(self, text="Ingrese la IP del Servidor SQL Server.\nEjemplo: 10.0.0.15 o 192.168.1.50", 
                     text_color="gray", font=("Roboto", 12)).pack(pady=5)

        # Input
        self.entry_ip = ctk.CTkEntry(self, width=250, height=35, placeholder_text="0.0.0.0")
        self.entry_ip.pack(pady=20)
        
        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color=Colors.DANGER, width=100, command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Guardar Configuración", fg_color=Colors.SUCCESS, width=150, command=self.save).pack(side="left", padx=10)

    def load_current(self):
        conf = ConfigManager.load_config()
        current_ip = conf.get('server_ip', '')
        self.entry_ip.insert(0, current_ip)

    def save(self):
        ip = self.entry_ip.get().strip()
        
        # Simple Validacion IP regex
        ip_regex = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        
        if not ip:
            messagebox.showerror("Error", "La IP no puede estar vacía")
            return
            
        if ip != "localhost" and ip != "(local)" and not re.match(ip_regex, ip):
             if not messagebox.askyesno("Advertencia", "El formato de IP parece inusual. ¿Desea guardar de todas formas?"):
                 return

        if ConfigManager.save_config(ip):
            messagebox.showinfo("Éxito", f"Configuración guardada: {ip}\nPor favor reinicie la aplicación o reintente el login.")
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar el archivo de configuración")
