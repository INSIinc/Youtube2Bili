import os
import youtube_dl
import asyncio
from pyppeteer import launch
from datetime import datetime
from Youtube2Bili.tools import BilingualSubtitleMerger,remove_invalid_urls
import os
from bilibili_toolman.bilisession.web import BiliSession
from bilibili_toolman.bilisession.common.submission import Submission
from PIL import Image
import time
from typing import List
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class YouTube2Bili:
    def __init__(self, blogger_urls, output_directory,bilibili_token, max_age_days=7, polling_interval=3600,):
        self.blogger_urls = blogger_urls
        self.output_directory = output_directory
        self.max_age_days = max_age_days
        self.bilibili_token=bilibili_token
        self.polling_interval = polling_interval
        self.downloaded_videos_file = os.path.join(output_directory, "downloaded_videos.txt")
    def update_config(self, blogger_urls, output_directory, bilibili_token,max_age_days, polling_interval):
        logger.info("信息更新")
        self.blogger_urls = blogger_urls
        self.output_directory = output_directory
        self.bilibili_token=bilibili_token
        self.max_age_days = max_age_days
        self.polling_interval = polling_interval
        self.downloaded_videos_file = os.path.join(output_directory, "downloaded_videos.txt")
    def process_video(self,video_title:str,video_path:str,video_desc:str,video_link:str,video_cover:str,video_tags:List[str]):
        session = BiliSession.from_base64_string(self.bilibili_token) 
        endpoint_1,cid_1 = session.UploadVideo(video_path)
        submission = Submission(
        title=video_title,
        desc=video_desc+f'\n来源:{video_link}'
        )
        submission.videos.append(
            Submission(
                title=video_title,
                video_endpoint=endpoint_1
            )
        )
        cover = session.UploadCover(video_cover)
        submission.description=video_desc+f'\n来源:{video_link}'
        submission.cover_url = cover['data']['url']
        submission.source = video_link
        submission.tags.append('转载')
        for tag in video_tags:
            submission.tags.append(tag)
        submission.thread = 122
        session.SubmitSubmission(submission,seperate_parts=False)
    async def get_blogger_videos(self, blogger_url):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(blogger_url)
        await asyncio.sleep(5)  # 添加延迟以确保页面完全加载
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
    def download_videos(self, video_links):
        ydl_opts = {
            'outtmpl': os.path.join(self.output_directory,'%(title)s','%(title)s.%(ext)s'),
            'format': 'best', 
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'zh-Hans'],
            'writethumbnail': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_links= remove_invalid_urls(video_links)
            for link in video_links:
                if link in self.downloaded_videos_url:
                    logger.info("视频已下载，跳过")
                    continue
                else:
                    logger.info("抓取视频信息中")
                    video_info = ydl.extract_info(link, download=False)
                    logger.info("信息抓取完毕")
                    if self.is_video_recent(video_info):
                        # subtitle=video_info['automatic_captions']
                        # subtitle_urls = [subtitle['zh-Hans'][4]['url'],subtitle['en'][4]['url']]
                        logger.info("视频下载中")
                        ydl.download([link])
                        logger.info("写入视频列表txt")
                        with open(self.downloaded_videos_file, "a") as f:
                            f.write(link + "\n")
                        
                        subtitle_ext = 'vtt'
                        subtitle_filename_en = os.path.splitext(ydl.prepare_filename(video_info))[0] +'.en' f'.{subtitle_ext}'
                        subtitle_filename_zh = os.path.splitext(ydl.prepare_filename(video_info))[0] +'.zh-Hans' f'.{subtitle_ext}'
                        output_subtitle=os.path.splitext(ydl.prepare_filename(video_info))[0] + f'.{subtitle_ext}'
                        video_path = ydl.prepare_filename(video_info)
                        logger.info("处理封面中")
                        [Image.open(os.path.join(os.path.dirname(video_path), f)).save(os.path.join(os.path.dirname(video_path), os.path.splitext(f)[0] + ".png"))  for f in os.listdir(os.path.dirname(video_path)) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif",".webp"))]
                        cover=os.path.splitext(ydl.prepare_filename(video_info))[0] + f'.png'
                        # ydl.download(subtitle_urls, outtmpl=subtitle_filename)
                        # logger.info("处理字幕中")
                        # BilingualSubtitleMerger.merge(subtitle_filename_en,subtitle_filename_zh,output_subtitle)
                        logger.info("清除多余文件中")
                        # os.remove(subtitle_filename_en)
                        # os.remove(subtitle_filename_zh)
                        [os.remove(f) for f in os.listdir(os.path.dirname(video_path)) if os.path.isfile(f) and not f.endswith('.png') and f.endswith(('.jpg', '.jpeg', '.bmp', '.gif','webp'))]
                        # 新增代码：处理视频文件，上传到 Bilibili 并删除本地文件
                        logger.info("正在发布至B站")
                        self.process_video(video_info['title'], video_path,video_info['description'],link,cover,video_info['tags'])
               

    def run(self):
        if not os.path.exists(self.downloaded_videos_file):
            with open(self.downloaded_videos_file, "w") as f:
                f.write("")
        with open(self.downloaded_videos_file, "r") as f:
            self.downloaded_videos_url = set(line.strip() for line in f.readlines())
        while True:
            if len(self.blogger_urls)==0:
                logger.warning("博主url为空")
            else:
                for blogger_url in self.blogger_urls:
                    logger.critical(f'处理博主：{blogger_url}')
                    video_links = asyncio.get_event_loop().run_until_complete(self.get_blogger_videos(blogger_url))
                    self.download_videos(video_links)
            time.sleep(self.polling_interval)



