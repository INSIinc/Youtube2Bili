import json
from watchdog.events import FileSystemEventHandler

class ConfigHandler(FileSystemEventHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_file=None, onConfigUpdateCallBacks=None):
        if config_file is not None and not hasattr(self, 'config_file'):
            self.config_file = config_file
            self.onConfigUpdateCallBacks = onConfigUpdateCallBacks or []
            self.config = {}
            self.reload_config()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.config_file):
            self.reload_config()
    @classmethod
    def instance(cls,config_file=None,onConfigUpdateCallBacks=None):
        return cls(config_file,onConfigUpdateCallBacks)
    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        return self.config

    def reload_config(self):
        self.config = self.load_config()
        for onConfigUpdate in self.onConfigUpdateCallBacks:
            onConfigUpdate()
