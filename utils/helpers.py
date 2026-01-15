from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import requests

def load_image_from_url(url, size=(100, 100)):
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(Qt.GlobalColor.lightGray)
    if not url or url == 'N/A': return pixmap
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap.fromImage(image)
    except: pass
    return pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
