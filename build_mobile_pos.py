import os
import sys
import subprocess
import shutil

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")

def main():
    PROJECT_NAME = "MiniERP_Mobile_POS_Server"
    ENTRY_POINT = "mobile_pos.py"
    
    print(f"--- Iniciando empaquetado de {PROJECT_NAME} ---")

    # 1. Instalar dependencias
    run_command("python -m pip install pyinstaller flask flask-cors qrcode Pillow pyodbc reportlab jinja2")

    # 2. Limpiar
    for folder in ['build_mobile', 'dist_mobile']:
        if os.path.exists(folder):
            try: shutil.rmtree(folder)
            except: pass

    # 3. PyInstaller
    separator = ";" if sys.platform == "win32" else ":"
    
    # IMPORTANTE: Incluir la carpeta templates para que Flask encuentre el index.html
    pyinstaller_cmd = [
        "python", "-m", "PyInstaller",
        "--onedir",
        f"--name={PROJECT_NAME}",
        f"--add-data=templates{separator}templates",
        f"--add-data=src{separator}src",
        f"--add-data=config.json{separator}.",
        "--collect-all=flask",
        "--collect-all=qrcode",
        ENTRY_POINT
    ]

    print("Ejecutando PyInstaller...")
    run_command(" ".join(pyinstaller_cmd))

    # 4. Mover a la carpeta dist principal para comodidad del usuario
    final_dest = os.path.join("dist", PROJECT_NAME)
    if os.path.exists(final_dest):
        shutil.rmtree(final_dest)
    
    if os.path.exists(os.path.join("dist", PROJECT_NAME)):
         shutil.move(os.path.join("dist", PROJECT_NAME), final_dest)

    print(f"\n✅ SERVIDOR MÓVIL GENERADO EN: dist/{PROJECT_NAME}")

if __name__ == "__main__":
    main()
