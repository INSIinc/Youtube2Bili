import os
import asyncio
from pyppeteer import launch
from datetime import datetime
from Youtube2Bili.tools import BilingualSubtitleMerger,remove_invalid_urls,is_valid_url,ChatbotWrapper
import os
from bilibili_toolman.bilisession.web import BiliSession
from bilibili_toolman.bilisession.common.submission import Submission
from PIL import Image
import time
import yt_dlp as youtube_dl
from typing import List
from Youtube2Bili.config_handler import ConfigHandler
import logging
import coloredlogs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
fmt = '%(asctime)s %(levelname)s %(message)s'
coloredlogs.install(level='INFO', logger=logger, fmt=fmt)

class YouTube2Bili:
    def __init__(self, ):
        self.video_downloaded = False
        self.blogger_urls = []
        self.output_directory = ''
        self.max_age_days = 0
        self.bilibili_token=''
        self.polling_interval = 0
        self.output_directory=''
        self.max_video_size_mb=0
        self.ffmpeg_path=''
        self.max_downloads_per_blogger=0
        self.downloaded_videos_file = os.path.join(self.output_directory, "downloaded_videos.txt")
        self.outdate_videos_file=os.path.join(self.output_directory,"outdate_videos.txt") 
           
    def update_config(self):
        logger.info("信息更新")
        self.blogger_urls = ConfigHandler.instance().config['blogger_urls']
        self.output_directory = ConfigHandler.instance().config['output_directory']
        self.bilibili_token=ConfigHandler.instance().config['bilibili_token']
        self.max_age_days = ConfigHandler.instance().config['max_age_days']
        self.polling_interval = ConfigHandler.instance().config['polling_interval']
        self.ffmpeg_path=ConfigHandler.instance().config['ffmpeg_path']
        self.max_video_size_mb = ConfigHandler.instance().config['max_video_size_mb']
        self.max_downloads_per_blogger=ConfigHandler.instance().config['max_downloads_per_blogger']
        self.downloaded_videos_file = os.path.join(self.output_directory, "downloaded_videos.txt")
        self.outdate_videos_file=os.path.join(self.output_directory,"outdate_videos.txt")  
    def progress_hook(self, status_info):
        if status_info['status'] == 'finished':
            self.video_downloaded = True
            logger.critical(f"视频下载完成: {status_info['filename']}")
    def process_video(self,video_title:str,video_path:str,video_desc:str,video_link:str,video_cover:str,video_tags:List[str]):
        session = BiliSession.from_base64_string(self.bilibili_token) 
        endpoint_1,cid_1 = session.UploadVideo(video_path)
        logger.info("GPT正在处理标题...")
        video_title=ChatbotWrapper.instance().ask(f'把这段话改写成有趣且富有吸引力，能够激发好奇心和学习欲望的中文标题，不超过20个字：{video_title}')
        logger.info("标题处理完毕！")
        logger.info("GPT正在生成描述...")
        video_desc=ChatbotWrapper.instance().ask(f'把这段话改写成有趣活泼、生动形象、简洁清晰的地道中文：{video_desc}')
        logger.info("描述生成完毕！")
        logger.info("GPT正在生成标签...")
        tags=ChatbotWrapper.instance().ask(f'{video_desc}用中文从以上文本中总结出不多于5个关键词，并用,隔开')
        tags=tags.split(',')
        logger.info("标签生成完毕！")
        logger.info("准备提交视频...")
        submission = Submission(
        title=video_title,
        desc=video_desc
        )
        submission.videos.append(
            Submission(
                title=video_title,
                video_endpoint=endpoint_1
            )
        )
        cover = session.UploadCover(video_cover)
        submission.description=video_desc
        submission.cover_url = cover['data']['url']
        submission.source = video_link
        submission.tags.append('转载')
        for tag in tags:
            submission.tags.append(tag)
        submission.thread = 122
        logger.info(session.SubmitSubmission(submission,seperate_parts=False))
        logger.info("写入视频列表txt...")
        with open(self.downloaded_videos_file, "a") as f:
            f.write(video_link + "\n")
        logger.info(f"B站上传完毕:{video_title}")
        
    async def get_blogger_videos(self, blogger_url):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(blogger_url)
        await asyncio.sleep(3)  # 添加延迟以确保页面完全加载
        video_links = await page.evaluate('''() => {
            const videoElements = document.querySelectorAll('#video-title-link');
            return Array.from(videoElements).map(video => video.href);
        }''')
        await browser.close()
        return video_links
    def is_video_recent(self, video_info):
        upload_date = datetime.strptime(video_info['upload_date'], '%Y%m%d')
        days_since_upload = (datetime.now() - upload_date).days
        return days_since_upload <= self.max_age_days
    def download_videos(self, video_link):
        self.video_downloaded = False  # 重置下载状态
        if not is_valid_url(video_link):
            logger.warning(f"{video_link}URL不合法！")
            return
        max_filesize = self.max_video_size_mb * 1024 * 1024
        ydl_opts = {
            'outtmpl': os.path.join(self.output_directory, '%(title)s', '%(title)s.%(ext)s'),
            'format': 'best',
            'writesubtitles': True,
            'max_filesize': max_filesize,
            'subtitleslangs': ['en', 'zh-Hans'],
            'writethumbnail': True,
            'writeinfojson': True,
            'embedsubtitles': True,
            'ffmpeg_location': self.ffmpeg_path,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{'key': 'FFmpegEmbedSubtitle'}],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if video_link in self.downloaded_videos_url or video_link in self.outdate_videos_url:
                logger.info("视频已下载或过时，跳过！")
                return
            else:
                logger.info("抓取视频信息中...")
                video_info = ydl.extract_info(video_link, download=False)
                logger.info("信息抓取完毕！")
                if self.is_video_recent(video_info):
                    logger.info("视频下载中...")
                    ydl.download([video_link])
                    if self.video_downloaded:
                        video_path = ydl.prepare_filename(video_info)
                        logger.info("处理封面中")
                        [Image.open(os.path.join(os.path.dirname(video_path), f)).save(os.path.join(os.path.dirname(video_path), os.path.splitext(f)[0] + ".png"))  for f in os.listdir(os.path.dirname(video_path)) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif",".webp"))]
                        cover=os.path.splitext(ydl.prepare_filename(video_info))[0] + f'.png'
                        logger.info("清除多余文件中")
                        [os.remove(os.path.join(os.path.dirname(video_path), f)) for f in os.listdir(os.path.dirname(video_path)) if os.path.isfile(os.path.join(os.path.dirname(video_path), f)) and not f.endswith('.png') and f.endswith(('.jpg', '.jpeg', '.bmp', '.gif', 'webp'))]
                        logger.info("正在发布至B站")
                        self.process_video(video_info['title'], video_path,video_info['description'],video_link,cover,video_info['tags'])
                        os.remove(video_path)
                    else:    
                        logger.info(f"可能由于文件大于{self.max_video_size_mb}MB，视频未下载，跳过后续处理")
                        return
                    if video_link in self.outdate_videos_url:
                            with open(self.outdate_videos_file, "w") as f:
                                for outlink in self.outdate_videos_url:
                                    if video_link != outlink:
                                        f.write(outlink) 
                else:
                    with open(self.outdate_videos_file, "a") as f:
                        f.write(video_link + "\n")

    def run(self):
        if not os.path.exists(self.downloaded_videos_file):
            with open(self.downloaded_videos_file, "w") as f:
                f.write("")
        if not os.path.exists(self.outdate_videos_file):
            with open(self.outdate_videos_file, "w") as f:
                f.write("")
        
        while True:
            with open(self.downloaded_videos_file, "r") as f:
                self.downloaded_videos_url = set(line.strip() for line in f.readlines())
            with open(self.outdate_videos_file,"r")as f:
                self.outdate_videos_url=set(line.strip() for line in f.readlines())
            if len(self.blogger_urls)==0:
                logger.warning("博主url为空")
            else:
                
                for blogger_url in self.blogger_urls:
                    logger.critical(f'处理博主：{blogger_url}')
                    video_links = asyncio.get_event_loop().run_until_complete(self.get_blogger_videos(blogger_url))
                    video_links=remove_invalid_urls(video_links)
                    # 添加计数器
                    downloaded_count = 0
                    for link in video_links:
                        if downloaded_count >= self.max_downloads_per_blogger:
                            logger.critical(f"已达到博主 {blogger_url} 的最大下载个数，跳过剩余视频。")
                            break
                        self.download_videos(link)
                        if self.video_downloaded:
                            downloaded_count += 1
                        
                        
                    
            
            
            time.sleep(self.polling_interval)



