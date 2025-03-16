import os
import subprocess
import logging
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

URL = "https://aoklivestrim.com/wp-json/purim/v1/display"

# **הורדת Chromium והגדרת נתיב**
CHROMIUM_PATH = "/tmp/chrome-linux/chrome"

def install_chromium():
    """הורדת Chromium לשרת Render אם הוא לא קיים"""
    if not os.path.exists(CHROMIUM_PATH):
        logging.info("Downloading Chromium...")
        subprocess.run([
            "bash", "-c",
            "mkdir -p /tmp/chrome-linux && "
            "curl -Lo /tmp/chrome-linux/chrome.zip https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && "
            "unzip /tmp/chrome-linux/chrome.zip -d /tmp/chrome-linux && "
            "chmod +x /tmp/chrome-linux/chrome"
        ], check=True)
        logging.info("Chromium installed successfully.")
    else:
        logging.info("Chromium is already installed.")

install_chromium()  # **מריץ את ההתקנה לפני שהשרת מתחיל לפעול**

def get_data_using_selenium():
    """שולף נתונים מהקישור באמצעות דפדפן אמיתי (Selenium)"""
    logging.info("Launching Chromium browser...")

    chrome_options = Options()
    chrome_options.binary_location = CHROMIUM_PATH  # **הגדרת הנתיב ל-Chromium**
    chrome_options.add_argument("--headless")  # הרצת הדפדפן ללא ממשק גרפי
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info(f"Navigating to {URL}...")
    driver.get(URL)

    # המתנה לטעינת העמוד
    time.sleep(5)

    # קבלת תוכן העמוד
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
    app.run(host="0.0.0.0", port=8080)
