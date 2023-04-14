
import pysubs2
from urllib.parse import urlparse
from EdgeGPT import Chatbot as GPTBing, ConversationStyle
from revChatGPT.V3 import Chatbot as GPTAPI
from revChatGPT.V1 import Chatbot as GPTWeb
from Youtube2Bili.config_handler import ConfigHandler, logger
import bilibili_toolman
import inspect
import hashlib
import subprocess
import sys
class GPTBot:
    def __init__(self,id):
        self.chatbot = None
        self.busy = False
        self.name=f"GPT-{hashlib.sha1(id.encode()).hexdigest()[:8]}"
    def ask(self, prompt):
        logger.critical(f"{self.name}正在处理...")
        self.busy=True
    def is_available(self):
        pass
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
class ChatGPtWeb(GPTBot):
    def __init__(self,access_token):
        super().__init__(access_token)
        if access_token!=None:
            self.chatbot=GPTWeb(config={
            "access_token": access_token
        })
        self.name=f"web-{self.name}"
       
        
    def ask(self, prompt):
        super().ask(prompt)
        response = ""
        for data in self.chatbot.ask(prompt):
            response = data["message"]
        self.busy=False
        return response
        
class ChatGPTAPI(GPTBot):
    def __init__(self,api_key):
        super().__init__(api_key)
        self.chatbot = GPTAPI(api_key=api_key)
        self.name=f"api-{self.name}"
    def ask(self, prompt):
        super().ask(prompt)
        result=self.chatbot.ask(prompt)
        self.busy=False
        return result
    
class BingBot(GPTBot):
    def __init__(self,bing_cookies_path):
        super().__init__(bing_cookies_path)
        self.chatbot=GPTBing(cookiePath=bing_cookies_path)
        self.name=f"bing-{self.name}"
    async def ask(self, prompt):
        super().ask(prompt)
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
        self.busy=False
        return result
    
class Chatbots:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # You can also initialize attributes here if needed
        return cls._instance
    def __init__(self):
        pass
    @classmethod
    def instance(cls):
        return cls()
    def get_next_bot(self):
        bot = self.chatbots[self.current_bot_index]
        self.current_bot_index = (self.current_bot_index + 1) % len(self.chatbots)
        return bot
    async def ask(self, prompt):
        bot = self.get_next_bot()
        while bot.busy:
            bot = self.get_next_bot()
        if inspect.iscoroutinefunction(bot.ask):
            return await bot.ask(prompt)
        else:
            return bot.ask(prompt)
    def update(self):
        """
        更新访问令牌

        :param new_access_token: 新的访问令牌
        """
        logger.info("载入GPT...")
        self.chatbots=[]
        self.current_bot_index = 0
        api_keys= ConfigHandler.instance().config['api_keys']
        access_tokens=ConfigHandler.instance().config['access_tokens']
        cookies_pathes=ConfigHandler.instance().config['bing_cookies_pathes']
        for key in api_keys:
            logger.info("载入chatgpt api")
            self.chatbots.append(ChatGPTAPI(key))
        for token in access_tokens:
            logger.info("载入chatgpt access_token")
            self.chatbots.append(ChatGPtWeb(token))
        for cookies in cookies_pathes:
            logger.info("载入bing cookies")
            self.chatbots.append(BingBot(cookies))
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
      
