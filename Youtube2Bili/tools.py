
import pysubs2
from urllib.parse import urlparse
from revChatGPT.V1 import Chatbot
from Youtube2Bili.config_handler import ConfigHandler
class ChatbotWrapper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # You can also initialize attributes here if needed
        return cls._instance

    def __init__(self,access_token=None):
        if access_token!=None:
            self.chatbot = Chatbot(config={
            "access_token": access_token
        })
        

    @classmethod
    def instance(cls, access_token=None):
        return cls(access_token)

    def ask(self, prompt):
        """
        询问 Chatbot

        :param prompt: 询问内容
        :return: Chatbot 的回答
        """
        response = ""
        for data in self.chatbot.ask(prompt):
            response = data["message"]
        return response

    def update_access_token(self):
        """
        更新访问令牌

        :param new_access_token: 新的访问令牌
        """
        self.chatbot = Chatbot(config={
            "access_token": ConfigHandler.instance().config['access_token']
        })


def remove_invalid_urls(urls):
    for url in urls:
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                # URL is valid
                continue
        except ValueError:
            pass
        # URL is invalid, remove it from list
        urls.remove(url)
    return urls

class BilingualSubtitleMerger:
    @staticmethod
    def merge(en_subs_path, zh_subs_path, output_path):
        # 读取英文字幕和中文字幕文件
        en_subs = pysubs2.load(en_subs_path, encoding='utf-8')
        zh_subs = pysubs2.load(zh_subs_path, encoding='utf-8')

        # 合并字幕
        for en_line, zh_line in zip(en_subs, zh_subs):
            # 在英文字幕和中文字幕的文本前面添加"[en]"和"[zh]"标记
            en_line.text = f"[en]{en_line.text}"
            zh_line.text = f"[zh]{zh_line.text}"
            # 合并英文字幕和中文字幕
            en_line.text += f"\n{zh_line.text}"
            # 将合并后的文本设置为英文字幕的文本
            en_line.text = en_line.text.strip()

        # 将合并后的双语字幕保存到新文件中
        if en_subs_path.lower().endswith('.srt'):
            file_type = 'srt'
        elif en_subs_path.lower().endswith('.vtt'):
            file_type = 'vtt'
        else:
            raise ValueError("Unsupported file format")
        en_subs.save(output_path,encoding='utf-8')
      
