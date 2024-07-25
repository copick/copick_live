import json
import os

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.getcwd(), "copick_live.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.copick_config_path = self.config.get("copick_config_path")
        self.counter_file_path = self.config.get("counter_file_path")
        self.cache_root = self.config.get("cache_root")
        
    def get(self, key, default=None):
        return self.config.get(key, default)

config = None

def get_config(config_path=None):
    global config
    if config is None or config_path:
        config = Config(config_path)
    return config
