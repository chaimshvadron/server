import os
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CHROMIUM_PATH = "/tmp/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver"

def install_chromium():
    """מוריד ומתקין את Chromium ו-ChromeDriver בסביבה עם מגבלות זיכרון"""
    logging.info("Downloading and setting up Chromium...")

    try:
        # ✅ ניקוי קבצים ישנים
        subprocess.run(["rm", "-rf", "/tmp/chrome-linux", "/tmp/chrome.zip", "/tmp/chromedriver.zip"], check=False)

        # ✅ שימוש בקישור אמין יותר להורדת Chromium
        chromium_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
        chromium_path = "/tmp/chrome.deb"
        
        subprocess.run(["curl", "-Lo", chromium_path, chromium_url], check=True)

        # ✅ בדיקה שהקובץ באמת ירד כמו שצריך
        if not os.path.exists(chromium_path) or os.stat(chromium_path).st_size < 10_000_000:
            raise Exception("Chromium download failed or file is too small!")

        # ✅ פריסת Chromium
        subprocess.run(["dpkg", "-x", chromium_path, "/tmp/chrome-linux"], check=True)

        os.chmod(CHROMIUM_PATH, 0o755)
        logging.info("Chromium installed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error installing Chromium: {e}")
        raise e

if __name__ == '__main__':
    install_chromium()
