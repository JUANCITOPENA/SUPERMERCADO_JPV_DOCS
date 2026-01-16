import requests
from PIL import Image
from io import BytesIO

class ImageLoader:
    @staticmethod
    def load_image_data(url):
        """
        Descarga la imagen y devuelve un objeto PIL.Image.
        No crea objetos CTkImage aquí para mantener la seguridad entre hilos.
        """
        if not url or url == 'N/A':
            return None
        
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                return img
        except Exception as e:
            print(f"Error loading image {url}: {e}")
        return None