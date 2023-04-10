## Response:
# YouTube2Bili 📹🚀🚀

Are you a super fan of YouTubers? Are you waiting for your favorite YouTuber to release a new video every day? Do you want to publish these videos on Bilibili, the largest video sharing platform in China?

Then you need YouTube2Bili 📹🚀🚀, a Python script that can easily download videos from a specified YouTuber to your local computer and publish them to Bilibili. 😍

## Install dependencies

Before you start using it, run the following command to install the required Python libraries:

```
pip install watchdog youtube_dl asyncio pyppeteer bilibili_toolman Pillow
```

## Usage

1. Clone the project: 💻

   ```bash
   git clone https://github.com/your_username/YouTube2Bili.git
   ```

2. Enter the project directory: 📂

   ```bash
   cd YouTube2Bili
   ```

3. Modify the configuration file: 🛠️

   Open the `config.json` file and modify it according to your needs. You need to provide the following information:

   * `blogger_urls`: a list of URLs of the YouTubers whose videos you want to download 🌐
   * `output_directory`: the output directory where the downloaded videos and subtitle files will be saved 📂
   * `bilibili_token`: Bilibili's access token, used to publish videos 🚀
   * `max_age_days`: download only the videos that were released in the past few days 📅
   * `polling_interval`: the time interval (in seconds) to check for new videos ⏰

4. Run the script: 🚀

   Run the following command to start the script:

   ```css
   python main.py
   ```

   The script will periodically check the channel of the YouTuber you specified to find new videos and download them to your local computer. It will then publish the videos to Bilibili.

   If you want to run the script in the background, use the `nohup` command:

   ```bash
   nohup python main.py &
   ```

   This will run the script in the background and write the output to the `nohup.out` file.

## Notes

* This script depends on the `youtube_dl` library to download YouTube videos. If you encounter download issues, please refer to the documentation of that library for more information. 📖

* This script uses the asyncio and pyppeteer libraries to retrieve video links from the specified YouTuber's channel. These libraries may require additional dependencies to be installed. If you encounter errors when running the script, adjust according to the error messages you receive. 🔍

* This script uses the `watchdog` library to monitor changes to the configuration file. If you want to change the configuration, make sure to save the changes in the specified configuration file. If you encounter configuration issues when running the script, please refer to the error messages you receive for help.

