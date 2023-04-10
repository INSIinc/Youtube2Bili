## Response:
# YouTube2Bili 📹🚀🚀

你是不是一个 YouTube 上的超级粉丝？你是不是每天都在等待你最喜欢的 YouTuber 发布新视频？你是不是想将这些视频发布到中国最大的视频分享平台 Bilibili 上？

那么，你就需要使用 YouTube2Bili 📹🚀🚀，这是一个 Python 脚本，可以轻松地将指定 YouTuber 的视频下载到本地并发布到 Bilibili。😍

## 安装依赖

在你开始使用之前，请先运行以下命令来安装需要的 Python 库：

```
pip install watchdog youtube_dl asyncio pyppeteer bilibili_toolman Pillow
```

## 使用方法

1. 克隆项目：💻

   ```bash
   git clone https://github.com/your_username/YouTube2Bili.git
   ```

2. 进入项目目录：📂

   ```bash
   cd YouTube2Bili
   ```

3. 修改配置文件：🛠️

   打开 `config.json` 文件并根据您的需要进行修改。您需要提供以下信息：

   * `blogger_urls`: 您要下载视频的 YouTuber 的 URL 列表 🌐
   * `output_directory`: 下载视频和字幕文件的输出目录 📂
   * `bilibili_token`: Bilibili 的访问令牌，用于发布视频 🚀
   * `max_age_days`: 仅下载最近几天发布的视频 📅
   * `polling_interval`: 检查新视频的时间间隔（以秒为单位）⏰

4. 运行脚本：🚀

   运行以下命令以启动脚本：

   ```css
   python main.py
   ```

   脚本将定期检查您指定的 YouTuber 的频道以查找新视频，并将其下载到本地。然后，它会将视频发布到 Bilibili。

   如果您希望在后台运行脚本，请使用 `nohup` 命令：

   ```bash
   nohup python main.py &
   ```

   这将使脚本在后台运行，并将输出写入 `nohup.out` 文件。

## 注意事项

* 本脚本依赖于 `youtube_dl` 库来下载 YouTube 视频。如果您遇到下载问题，请查看该库的文档以了解更多信息。📖

* 本脚本使用 asyncio 和 pyppeteer 库来从指定 YouTuber 的频道中获取视频链接。这些库可能需要安装其他依赖项。如果您在运行脚本时遇到错误，请根据您收到的错误消息进行调整。🔍

* 本脚本使用 `watchdog` 库来监视配置文件的更改。如果您想更改配置文件，请确保将更改保存在指定的配置文件中。如果您在运行脚本时遇到配置问题，请查看配置文件的格式是否正确。

