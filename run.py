import sys
import os

# Agregar el directorio actual al path para que Python encuentre el paquete 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()