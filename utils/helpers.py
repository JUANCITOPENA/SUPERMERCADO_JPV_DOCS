# utils/helpers.py
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import requests
import io
from database import db

def load_image_from_url(url, size=(200, 200)):
    """Carga imagen desde URL con manejo de errores y placeholder."""
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(Qt.GlobalColor.lightGray)
    
    if not url or not url.startswith('http'):
        return pixmap

    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap.fromImage(image)
    except Exception as e:
        print(f"Error cargando imagen: {e}")
        
    return pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

def get_next_id(table_name, id_column):
    """Calcula el siguiente ID (Max + 1) para cualquier tabla."""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT ISNULL(MAX({id_column}), 0) + 1 FROM {table_name}")
        next_id = cursor.fetchone()[0]
        conn.close()
        return next_id
    except Exception as e:
        print(f"Error obteniendo ID: {e}")
        return 1