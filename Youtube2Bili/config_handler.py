import json
import logging
import coloredlogs
from watchdog.events import FileSystemEventHandler
import random
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
fmt = '%(asctime)s %(levelname)s %(message)s'
coloredlogs.install(level='INFO', logger=logger, fmt=fmt)
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
        with open(self.config_file, 'r',encoding="utf-8") as f:
            self.config = json.load(f)
        if not os.path.exists(self.config['output_directory']):
            os.mkdir(self.config['output_directory'])
        self.config['blogger_urls']=[]
        for blogger in self.config['bloggers']:
            self.config['blogger_urls'].append(f"https://www.youtube.com/@{blogger}/videos")
        if self.config['enable_shuffle']:
            logger.info("博主处理顺序已被随机调整！")
            random.shuffle(self.config['blogger_urls'])
        

    def reload_config(self):
        self.load_config()
        for onConfigUpdate in self.onConfigUpdateCallBacks:
            onConfigUpdate()
