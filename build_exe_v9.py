import os
import sys
import subprocess
import shutil

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        # sys.exit(result.returncode)

def main():
    # 1. Configuración de nombres
    PROJECT_NAME = "MiniERP_Supermercado_JPV_V9"
    ENTRY_POINT = "run.py"
    
    print(f"--- Iniciando empaquetado de {PROJECT_NAME} ---")

    # 2. Instalar dependencias necesarias para el build
    print("Instalando dependencias de build...")
    run_command("python -m pip install --upgrade pip")
    run_command("python -m pip install pyinstaller customtkinter Pillow pyodbc reportlab xlsxwriter matplotlib requests packaging tkcalendar")

    # 3. Limpiar compilaciones anteriores
    print("Limpiando carpetas temporales...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except:
                print(f"No se pudo borrar {folder}, asegurese de cerrar el programa.")

    # 4. Comando de PyInstaller
    separator = ";" if sys.platform == "win32" else ":"

    pyinstaller_cmd = [
        "python", "-m", "PyInstaller",
        "--noconsole",
        "--onedir",
        f"--name={PROJECT_NAME}",
        f"--add-data=src{separator}src",
        f"--add-data=imagenes_proyecto{separator}imagenes_proyecto",
        f"--add-data=docs{separator}docs",
        f"--add-data=config.json{separator}.",
        "--collect-all=customtkinter",
        "--collect-all=tkcalendar",
        "--hidden-import=PIL._tkinter_finder",
        ENTRY_POINT
    ]

    print("Ejecutando PyInstaller...")
    run_command(" ".join(pyinstaller_cmd))

    # 5. Verificar resultado
    exe_path = os.path.join("dist", PROJECT_NAME, f"{PROJECT_NAME}.exe")
    if os.path.exists(exe_path):
        print("\nSUCCESS: Ejecutable generado en: " + exe_path)
        print("FOLDER: La carpeta completa para distribuir es: " + os.path.abspath(os.path.join('dist', PROJECT_NAME)))
    else:
        print("\nERROR: No se pudo generar el ejecutable.")

if __name__ == "__main__":
    main()
