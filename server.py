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

# **הגדרת נתיב Chromium**
CHROMIUM_PATH = "/usr/bin/chromium-browser"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

def install_chromium():
    """התקנת Chromium מ-APT במקום curl"""
    logging.info("Installing Chromium using apt-get...")
    subprocess.run([
        "bash", "-c",
        "apt-get update && "
        "apt-get install -y chromium-browser chromium-chromedriver && "
        "ln -s /usr/bin/chromium /usr/bin/chromium-browser"
    ], check=True)
    logging.info("Chromium and ChromeDriver installed successfully.")

install_chromium()  # **מתקין Chromium לפני שהשרת מתחיל לפעול**

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

    service = Service(CHROMEDRIVER_PATH)  # **משתמש ב-ChromeDriver**
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
