import customtkinter as ctk
from src.views.login import LoginWindow

def main():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    
    # Store app instance globally or in a scope that survives
    app = None

    def start_app(user_data):
        nonlocal app
        print(f"Login Success: {user_data}")
        
        import src.views.main_window as mw
        # Close login and open main
        app = mw.MainWindow(user_data)
        app.mainloop()

    login = LoginWindow(start_app)
    login.mainloop()

if __name__ == "__main__":
    main()
