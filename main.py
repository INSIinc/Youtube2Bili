import asyncio
from watchdog.observers import Observer
from Youtube2Bili.core import YouTube2Bili
from Youtube2Bili.config_handler import ConfigHandler
from Youtube2Bili.tools import Chatbots
async def main(config_file):    
    bots=Chatbots()
    downloader = YouTube2Bili()
    # 监听配置文件更改
    event_handler = ConfigHandler(config_file, [downloader.update_config,bots.update])
    
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    try:
        await downloader.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    asyncio.run(main("config.json"))
