
import customtkinter as ctk
from src.views.styles import Colors, Fonts
from src.controllers.auth_controller import AuthController
from tkinter import messagebox

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.controller = AuthController()
        self.on_login_success = on_login_success

        self.title("Login - Mini ERP Supermercado")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.configure(fg_color=Colors.BACKGROUND)

        # Frame
        self.frame = ctk.CTkFrame(self, fg_color=Colors.PANEL, corner_radius=10)
        self.frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Title
        self.label_title = ctk.CTkLabel(self.frame, text="BIENVENIDO", font=Fonts.TITLE, text_color=Colors.TEXT)
        self.label_title.pack(pady=(40, 20))

        # User
        self.entry_user = ctk.CTkEntry(self.frame, placeholder_text="Usuario", height=40, font=Fonts.BODY)
        self.entry_user.pack(pady=10, padx=20, fill="x")

        # Password
        self.entry_pass = ctk.CTkEntry(self.frame, placeholder_text="Contraseña", show="*", height=40, font=Fonts.BODY)
        self.entry_pass.pack(pady=10, padx=20, fill="x")

        # Button
        self.btn_login = ctk.CTkButton(self.frame, text="INICIAR SESIÓN", height=40, 
                                       font=Fonts.BUTTON, fg_color=Colors.PRIMARY, hover_color="#144a75",
                                       command=self.perform_login)
        self.btn_login.pack(pady=30, padx=20, fill="x")
        
        # Bind Enter key
        self.bind('<Return>', lambda event: self.perform_login())

    def perform_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        if not user or not pwd:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return

        result = self.controller.login(user, pwd)
        # result is (ID_USUARIO, ROL) if success, else None
        
        if result:
            self.destroy()
            self.on_login_success({'id': result[0], 'rol': result[1], 'username': user})
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
