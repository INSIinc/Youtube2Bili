
import pysubs2
from urllib.parse import urlparse
from EdgeGPT import Chatbot, ConversationStyle
from Youtube2Bili.config_handler import ConfigHandler, logger
import bilibili_toolman
import subprocess
import sys

def get_bili_login_token(sessdata, bili_jct):
    """
    运行 bilibili_toolman 命令，并返回去除“保存登录凭据”、空格和换行符后的输出结果。
    """
    # 构造命令行命令
    # command = ["python", "-m", "bilibili_toolman", "--save", "--cookies", f"\"SESSDATA={sessdata};bili_jct={bili_jct}\""]
    command=f"python -m bilibili_toolman --save --cookies \"SESSDATA={sessdata};bili_jct={bili_jct}\""
    # 运行命令行命令，并捕获输出结果
    # 假设命令行输出是gbk编码
    output = subprocess.check_output(command) # 不指定encoding参数，返回字节序列
    output = str(output).split('\\n')[2].split('\\r')[0] # 用utf-8编码编码字符串，返回字节序列
    # 返回处理后的输出结果
    return output
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
class BingbotWrapper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # You can also initialize attributes here if needed
        return cls._instance

    def __init__(self,bing_cookies_path=None):
        if bing_cookies_path!=None:
            self.chatbot = Chatbot(cookiePath=bing_cookies_path)
        
    @classmethod
    def instance(cls, bing_cookies_path=None):
        return cls(bing_cookies_path)

    async def ask(self, prompt):
        """
        询问 Chatbot

        :param prompt: 询问内容
        :return: Chatbot 的回答
        """
        max_tries=5
        for i in range(max_tries):
            try:
                response=await self.chatbot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
                result=''
                for msg in response['item']['messages']:
                    if msg['author']=='bot':
                        result+=msg['text']
                break
            except Exception as e:
                logger.error(f"bingbot出错，错误{e}，重试第{i+1}次")
                if i==max_tries-1:
                    logger.error(f"GPT处理失败或拒绝处理，{response['item']['messages'][1]['hiddenText']}")
                    raise Exception("hiddenText")
        await self.chatbot.close()
        return result
    def update_cookies_path(self):
        """
        更新访问令牌

        """
        self.chatbot = Chatbot(cookiePath=ConfigHandler.instance().config['bing_cookies_path'])
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
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
      
