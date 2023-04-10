# YouTube2Bili 📹🚀🚀

你是否是每天都在等待你最喜欢的YouTuber发布新视频？你想把他们的精彩内容分享到中国最大的视频分享平台`Bilibili`上吗？

那么就来试试YouTube2Bili 📹🚀🚀 - 一个能够从任何你想要的YouTuber那里下载视频并上传到Bilibili的Python脚本！😍

## 安装

在使用 YouTube2Bili 之前，需要安装以下依赖库：

* [watchdog](https://pypi.org/project/watchdog/) - 监控配置文件的变化
* [youtube\_dl](https://pypi.org/project/youtube_dl/) - 从YouTube下载视频
* [asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html) 和 [pyppeteer](https://github.com/pyppeteer/pyppeteer) - 从指定YouTuber的频道中获取视频链接
* [bilibili\_toolman](https://pypi.org/project/bilibili-toolman/) - 上传视频到Bilibili
* [Pillow](https://pypi.org/project/Pillow/) - 处理视频缩略图

你可以通过运行以下命令安装这些依赖库：

```
pip install watchdog youtube_dl asyncio pyppeteer bilibili_toolman Pillow
```

## 使用

1. 克隆项目到你的电脑：

   ```bash
   git clone https://github.com/INSIinc/YouTube2Bili.git
   ```

2. 进入项目目录：

   ```bash
   cd YouTube2Bili
   ```

3. 修改配置文件：

   `config.json` 文件包含了 YouTube2Bili 所需的所有配置选项。你需要提供以下信息：

   * `blogger_urls`：你想要下载视频的 YouTuber 的 URL 列表 🌐
   * `output_directory`：下载的视频和字幕文件将保存的输出目录 📂
   * `bilibili_token`：Bilibili 的访问令牌，用于发布视频 🚀（具体配置方法参考bilibili\_toolman库）
   * `max_age_days`：仅下载最近几天发布的视频 📅
   * `polling_interval`：检查新视频的时间间隔（以秒为单位） ⏰

   需要注意的是：所有的字段都是必填的。如果你不填写，将无法使用脚本。

4. 运行脚本：

   运行以下命令以启动脚本：

   ```css
   python main.py
   ```

   脚本将定期检查你指定的 YouTuber 的频道以查找新视频并将它们下载到你的本地计算机。然后它会将这些视频发布到 Bilibili。

   如果你想在后台运行脚本，请使用 `nohup` 命令：

   ```bash
   nohup python main.py &
   ```

## Response:
5. 配置自动启动：

   如果你想在系统启动时自动启动 YouTube2Bili，可以在 Linux 或 macOS 上使用 `crontab`，在 Windows 上使用任务计划程序。以下是一个使用 `crontab` 的示例：

   1. 打开终端并输入以下命令：

      ```
      crontab -e
      ```

   2. 在打开的文件中添加以下行：

      ```lua
      @reboot cd /path/to/YouTube2Bili && python main.py >> /path/to/log/file.log 2>&1
      ```

      将 `/path/to/YouTube2Bili` 替换为你克隆 YouTube2Bili 的路径，将 `/path/to/log/file.log` 替换为你想要保存日志文件的路径。

   3. 保存并关闭文件。

6. 享受视频：

   现在，你已经成功地将 YouTuber 的视频分享到 Bilibili 了！😍

   你可以在 `output_directory` 中找到下载的视频和字幕文件，以及相应的缩略图文件。

## 配置文件示例

下面是一个配置文件示例：

```json
{
    "blogger_urls": [
        "https://www.youtube.com/@Fireship/videos",
        "https://www.youtube.com/@BrickExperimentChannel/videos"
    ],
    "output_directory": "/path/to/your/output/directory",
    "bilibili_token": "your_bilibili_access_token",
    "max_age_days": 7,
    "polling_interval": 3600
}
```


## 贡献

如果你想为这个项目做出贡献，欢迎提交 PR 或提出问题！

## 许可证

这个项目使用 [MIT 许可证](https://opensource.org/licenses/MIT)。

