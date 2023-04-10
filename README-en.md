## Response:
# YouTube2Bili 📹🚀🚀

Are you constantly waiting for your favorite YouTubers to release new videos every day? Do you want to share their exciting content on China's largest video sharing platform, Bilibili?

Then try YouTube2Bili 📹🚀🚀 - a Python script that can download videos from any YouTuber you want and upload them to Bilibili! 😍

## Installation

Before using YouTube2Bili, you need to install the following dependencies:

* [watchdog](https://pypi.org/project/watchdog/) - Monitor changes to configuration files
* [youtube\_dl](https://pypi.org/project/youtube_dl/) - Download videos from YouTube
* [asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html) and [pyppeteer](https://github.com/pyppeteer/pyppeteer) - Get video links from specified YouTuber's channel
* [bilibili\_toolman](https://pypi.org/project/bilibili-toolman/) - Upload videos to Bilibili
* [Pillow](https://pypi.org/project/Pillow/) - Process video thumbnails

You can install these dependencies by running the following command:

```
pip install watchdog youtube_dl asyncio pyppeteer bilibili_toolman Pillow
```

## Usage

1. Clone the project to your computer:

   ```bash
   git clone https://github.com/INSIinc/YouTube2Bili.git
   ```

2. Enter the project directory:

   ```bash
   cd YouTube2Bili
   ```

3. Modify the configuration file:

   The `config.json` file contains all the configuration options required for YouTube2Bili. You need to provide the following information:

   * `blogger_urls`: A list of URLs of YouTubers whose videos you want to download 🌐
   * `output_directory`: The output directory where downloaded videos and subtitle files will be saved 📂
   * `bilibili_token`: Bilibili access token for video publishing 🚀 (Refer to bilibili\_toolman library for detailed configuration)
   * `max_age_days`: Only download videos published in the last few days 📅
   * `polling_interval`: Time interval (in seconds) for checking new videos ⏰

   Please note that all fields are required. If you do not fill them out, the script will not work.

4. Run the script:

   Run the following command to start the script:

   ```css
   python main.py
   ```

   The script will periodically check the channels of the YouTubers you specified for new videos and download them to your local computer. Then it will publish these videos to Bilibili.

   If you want to run the script in the background, use the `nohup` command:

   ```bash
   nohup python main.py &
   ```

## Response:

5. Configure automatic startup:

   If you want to automatically start YouTube2Bili when the system starts up, you can use `crontab` on Linux or macOS and Task Scheduler on Windows. Here is an example of using `crontab`:

   1. Open a terminal and enter the following command:

      ```
      crontab -e
      ```

   2. Add the following line to the file that opens:

      ```lua
      @reboot cd /path/to/YouTube2Bili && python main.py >> /path/to/log/file.log 2>&1
      ```

      Replace `/path/to/YouTube2Bili` with

## Response:
the path where you cloned YouTube2Bili, and replace `/path/to/log/file.log` with the path where you want to save the log file.

3. Save and close the file.

4. Enjoy the videos:

   Now you have successfully shared YouTuber's videos to Bilibili! 😍

   You can find the downloaded videos and subtitle files, as well as the corresponding thumbnail files, in the `output_directory`.

## Configuration file example

Here is an example configuration file:

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

## Contribution

If you want to contribute to this project, feel free to submit a PR or raise an issue!

## License

This project is licensed under the [MIT license](https://opensource.org/licenses/MIT).

