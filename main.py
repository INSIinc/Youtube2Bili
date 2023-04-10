import os
import json

from watchdog.observers import Observer
from Youtube2Bili.core import YouTube2Bili
from Youtube2Bili.config_handler import ConfigHandler
from Youtube2Bili.tools import ChatbotWrapper
def main(config_file):    
    gpt=ChatbotWrapper()
    # print(gpt.ask("你好"))
    downloader = YouTube2Bili()
    # 监听配置文件更改
    event_handler = ConfigHandler(config_file, [downloader.update_config,gpt.update_access_token])
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
