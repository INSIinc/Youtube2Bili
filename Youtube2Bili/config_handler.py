from watchdog.events import FileSystemEventHandler
import json

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, config_file, updateDowner):
        self.config_file = config_file
        self.updateDownwer = updateDowner
        self.reload_config()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.config_file):
            self.reload_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        return config

    def reload_config(self):
        config = self.load_config()
        blogger_urls = config['blogger_urls']
        output_directory = config['output_directory']
        max_age_days = config['max_age_days']
        polling_interval = config['polling_interval']
        bilibili_token=config['bilibili_token']
        self.updateDownwer(blogger_urls, output_directory,bilibili_token, max_age_days, polling_interval)
