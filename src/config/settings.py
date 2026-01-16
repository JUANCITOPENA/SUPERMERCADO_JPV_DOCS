import json
import os

CONFIG_FILE = "config.json"

class ConfigManager:
    @staticmethod
    def get_config_path():
        # Asegura que el archivo se busque en la raíz del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, CONFIG_FILE)

    @staticmethod
    def load_config():
        path = ConfigManager.get_config_path()
        default_config = {"server_ip": "10.0.0.15"}
        
        if not os.path.exists(path):
            try:
                with open(path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
            except Exception as e:
                print(f"Error creando config: {e}")
                return default_config
        
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo config: {e}")
            return default_config

    @staticmethod
    def save_config(ip_address):
        path = ConfigManager.get_config_path()
        data = {"server_ip": ip_address}
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error guardando config: {e}")
            return False
