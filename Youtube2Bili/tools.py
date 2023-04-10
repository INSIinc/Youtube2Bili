
import pysubs2
from urllib.parse import urlparse

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
      