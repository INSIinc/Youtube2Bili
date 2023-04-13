import asyncio
import logging
import os
import time
from datetime import datetime
from typing import List
import shutil

import coloredlogs
import yt_dlp as youtube_dl
from bilibili_toolman.bilisession.common.submission import Submission
from bilibili_toolman.bilisession.web import BiliSession
from PIL import Image
from pyppeteer import launch

from Youtube2Bili.config_handler import ConfigHandler
from Youtube2Bili.tools import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
fmt = '%(asctime)s %(levelname)s %(message)s'
coloredlogs.install(level='INFO', logger=logger, fmt=fmt)

class YouTube2Bili:
    def __init__(self, ):
        self.video_downloaded = False
        self.max_age_days=None
        
        
    def update_config(self):
        logger.critical("加载config.json")
        self.output_directory = ConfigHandler.instance().config['output_directory']
        self.downloaded_videos_file = os.path.join(self.output_directory, "downloaded_videos.txt")
        self.outdate_videos_file=os.path.join(self.output_directory,"outdate_videos.txt")  
        self.polling_interval = ConfigHandler.instance().config['polling_interval']
        self.ffmpeg_path=ConfigHandler.instance().config['ffmpeg_path']
        self.max_video_size_mb = ConfigHandler.instance().config['max_video_size_mb']
        self.max_downloads_per_blogger=ConfigHandler.instance().config['max_downloads_per_blogger']
        self.sessdata=ConfigHandler.instance().config['sessdata']
        self.bili_jct=ConfigHandler.instance().config['bili_jct']
        self.title_prompt=ConfigHandler.instance().config['title_prompt']
        self.desc_prompt=ConfigHandler.instance().config['desc_prompt']
        self.blogger_urls = ConfigHandler.instance().config['blogger_urls']
        self.bili_login_token=get_bili_login_token(self.sessdata,self.bili_jct)
        self.session =BiliSession.from_base64_string(self.bili_login_token) 
        if not os.path.exists(self.downloaded_videos_file):
            with open(self.downloaded_videos_file, "w") as f:
                f.write("")
        if not os.path.exists(self.outdate_videos_file):
            with open(self.outdate_videos_file, "w") as f:
                f.write("")
       
        if self.max_age_days!=None and self.max_age_days!=ConfigHandler.instance().config['max_age_days']:
            logger.info("检测到max_age_days更新->重新生成缓存")
            with open(self.outdate_videos_file, "w") as f:
                f.write("")
        self.max_age_days = ConfigHandler.instance().config['max_age_days']
        with open(self.downloaded_videos_file, "r") as f:
                self.downloaded_videos_url = set(line.strip() for line in f.readlines())
        with open(self.outdate_videos_file,"r")as f:
            self.outdate_videos_url=set(line.strip() for line in f.readlines())
    def progress_hook(self, status_info):
        if status_info['filename'].endswith('.mp4')and status_info['status'] == 'finished':
            self.video_downloaded = True
            logger.critical(f"视频下载完成: {status_info['filename']}")
    async def process_video(self,video_title:str,video_path:str,video_desc:str,video_link:str,video_cover:str,video_tags:List[str]):
        logger.info(f"视频开始上传")
        max_tries=5
        for i in range(max_tries):
            try:
                endpoint_1,cid_1 = self.session.UploadVideo(video_path)
                break
            except Exception as e:
                logger.error(f"视频上传出错,{e}，重试第{i+1}次")
                if i==max_tries-1:
                    raise Exception("视频上传出错！")
        logger.info("GPT正在处理标题...")
        try:
            res=await BingbotWrapper.instance().ask(f'{self.title_prompt}{video_title}')
            video_title=res
        except Exception as e:
            if e=='hiddenText':
                pass
        
        logger.info(f"标题处理完毕:{video_title}")
        logger.info("GPT正在生成描述...")
        try:
            res=await BingbotWrapper.instance().ask(f'{self.desc_prompt}{video_desc}')
            video_desc=res
        except Exception as e:
            if e=='hiddenText':
                pass
        logger.info("描述生成完毕！")
        logger.info("GPT正在生成标签...")
        tags=[]
        try:
            res=await BingbotWrapper.instance().ask(f'{video_desc} 用中文从以上文本中总结出不多于5个关键词，并用“-”隔开，只需要输出结果，不要补充，不要解释')
            tags=res.split('-')
        except Exception as e:
            if e=='hiddenText':
                pass
        
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
        cover = self.session.UploadCover(video_cover)
        submission.description=video_desc
        submission.cover_url = cover['data']['url']
        submission.source = video_link
        submission.tags.append('转载')
        for tag in tags:
            submission.tags.append(tag)
        submission.thread = 122
        resp=self.session.SubmitSubmission(submission,seperate_parts=False)
        logger.info(resp)
        if resp['results'][0]['code']!=0:
            raise Exception(resp['results'][0]['message'])
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
    async def download_videos(self, video_link):
        self.video_downloaded = False  # 重置下载状态
        if not is_valid_url(video_link):
            logger.warning(f"{video_link}URL不合法！")
            return
        max_filesize = self.max_video_size_mb * 1024 * 1024
        ydl_opts = {
            'outtmpl': os.path.join(self.output_directory, '%(title)s', '%(title)s.%(ext)s'),
            'format': 'best',
            # 'writesubtitles': True,
            'max_filesize': max_filesize,
            # 'subtitleslangs': ['en', 'zh-Hans'],
            'writethumbnail': True,
            # 'writeinfojson': True,
            # 'embedsubtitles': True,
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
                    max_retries = 3 # 设置最大重试次数
                    for i in range(max_retries):
                        try:
                            ydl.download([video_link])
                            break # 如果成功下载，跳出循环
                        except Exception as e:
                            logger.error(f"{video_link}视频下载失败，错误信息：{e}")
                            if i == max_retries - 1: # 如果达到最大重试次数，返回
                                return

                    if self.video_downloaded:
                        video_path = ydl.prepare_filename(video_info)
                        logger.info("处理封面中...")
                        [Image.open(os.path.join(os.path.dirname(video_path), f)).save(os.path.join(os.path.dirname(video_path), os.path.splitext(f)[0] + ".png"))  for f in os.listdir(os.path.dirname(video_path)) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif",".webp"))]
                        cover=os.path.splitext(ydl.prepare_filename(video_info))[0] + f'.png'
                        logger.info("封面处理完毕！")
                        max_retries = 3 # 设置最大重试次数
                        for i in range(max_retries):
                            try:
                                await self.process_video(video_info['title'], video_path,video_info['description'],video_link,cover,video_info['tags'])
                                break
                            except Exception as e:
                                logger.error(f"{video_link}视频发布失败，错误信息：{e}，重试第{i+1}次")
                                
                                if i == max_retries - 1: # 如果达到最大重试次数，返回
                                    return
                                
                        
                        logger.info("清除已上传视频及文件...")
                        shutil.rmtree(os.path.dirname(video_path))
        
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

    async def run(self):
        
        while True:
            
            if len(self.blogger_urls)==0:
                logger.warning("博主url为空")
            else:
                
                for blogger_url in self.blogger_urls:
                    logger.critical(f'处理博主：{blogger_url}')
                    video_links = await self.get_blogger_videos(blogger_url)
                    video_links=remove_invalid_urls(video_links)
                    # 添加计数器
                    downloaded_count = 0
                    for link in video_links:
                        if downloaded_count >= self.max_downloads_per_blogger:
                            logger.critical(f"已达到博主 {blogger_url} 的最大下载个数，跳过剩余视频。")
                            break
                        await self.download_videos(link)
                        if self.video_downloaded:
                            downloaded_count += 1
                        
            remaining_time = self.polling_interval
            while remaining_time > 0:
                logger.info(f"等待 {remaining_time} 秒...")
                time.sleep(1)
                remaining_time -= 1
            logger.info("进入下一轮发布...")



