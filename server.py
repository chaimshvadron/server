import os
import logging
import subprocess
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

URL = "https://aoklivestrim.com/wp-json/purim/v1/display"

# **הגדרת נתיבים ל-Chromium ול-ChromeDriver**
CHROMIUM_PATH = "/tmp/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver"

def install_chromium():
    """מוריד ומתקין את Chromium ו-ChromeDriver בסביבה עם מגבלות זיכרון"""
    logging.info("Downloading and setting up Chromium...")

    try:
        # ✅ ניקוי קבצים ישנים
        subprocess.run(["rm", "-rf", "/tmp/chrome-linux", "/tmp/chrome.zip", "/tmp/chromedriver.zip"], check=False)

        # ✅ הורדת Chromium לגרסה קטנה יותר שמתאימה לשרתים מוגבלי זיכרון
        chromium_url = "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_122.0.6261.112-1_amd64.deb"
        chromium_path = "/tmp/chrome.deb"
        
        subprocess.run(["curl", "-Lo", chromium_path, chromium_url], check=True)
        
        if not os.path.exists(chromium_path) or os.stat(chromium_path).st_size < 10_000_000:
            raise Exception("Chromium download failed or file is too small!")

        # ✅ פריסת Chromium באופן ידני
        subprocess.run(["dpkg", "-x", chromium_path, "/tmp/chrome-linux"], check=True)

        # ✅ עדכון ההרשאות של Chromium
        os.chmod(CHROMIUM_PATH, 0o755)
        logging.info("Chromium installed successfully.")

        # ✅ הורדת ChromeDriver תואם
        chromedriver_url = "https://chromedriver.storage.googleapis.com/122.0.6261.112/chromedriver-linux64.zip"
        chromedriver_zip = "/tmp/chromedriver.zip"

        subprocess.run(["curl", "-Lo", chromedriver_zip, chromedriver_url], check=True)
        
        if not os.path.exists(chromedriver_zip) or os.stat(chromedriver_zip).st_size < 1_000_000:
            raise Exception("ChromeDriver download failed or file is too small!")

        # ✅ חילוץ ChromeDriver
        subprocess.run(["unzip", chromedriver_zip, "-d", "/tmp"], check=True)
        subprocess.run(["mv", "/tmp/chromedriver", CHROMEDRIVER_PATH], check=True)
        os.chmod(CHROMEDRIVER_PATH, 0o755)

        logging.info("ChromeDriver installed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error installing Chromium/ChromeDriver: {e}")
        raise e

def get_data_using_selenium():
    """שולף נתונים מהקישור באמצעות Selenium"""
    logging.info("Launching Chromium browser...")

    chrome_options = Options()
    chrome_options.binary_location = CHROMIUM_PATH
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x720")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info(f"Navigating to {URL}...")
    driver.get(URL)

    driver.implicitly_wait(10)

    page_source = driver.page_source
    driver.quit()

    return page_source

@app.route('/')
def home():
    return "Proxy Server is Running"

@app.route('/proxy', methods=['GET'])
def proxy():
    logging.info(f"Fetching data from URL: {URL} using Selenium...")
    try:
        data = get_data_using_selenium()
        return data, 200
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    install_chromium()  # **מוריד את Chromium ו-ChromeDriver לפני הפעלת השרת**
    app.run(host="0.0.0.0", port=8080)
