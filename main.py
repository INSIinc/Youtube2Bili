import os
import json

from watchdog.observers import Observer
from Youtube2Bili.core import YouTube2Bili
from Youtube2Bili.config_handler import ConfigHandler

def main(config_file):  
    # 读取配置文件
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    blogger_urls = config['blogger_urls']
    output_directory = config['output_directory']
    max_age_days = config['max_age_days']
    polling_interval = config['polling_interval']
    bilibili_token=config['bilibili_token']
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    downloader = YouTube2Bili(blogger_urls, output_directory,bilibili_token, max_age_days, polling_interval)
    # 监听配置文件更改
    event_handler = ConfigHandler(config_file, downloader.update_config)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    try:
        downloader.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main("config.json")
