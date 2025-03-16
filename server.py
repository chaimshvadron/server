import os
import logging
import requests
import subprocess
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

URL = "https://aoklivestrim.com/wp-json/purim/v1/display"

# **הגדרת נתיבים ל-Chromium ול-Chromedriver**
CHROMIUM_PATH = "/tmp/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver"

def install_chromium():
    """מוריד ומגדיר את Chromium ו-ChromeDriver בסביבת Render"""
    logging.info("Downloading and setting up Chromium...")

    try:
        subprocess.run([
            "bash", "-c",
            "mkdir -p /tmp/chrome-linux && "
            "curl -Lo /tmp/chrome-linux/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.112/linux64/chrome-linux64.zip && "
            "unzip /tmp/chrome-linux/chrome.zip -d /tmp/chrome-linux && "
            "chmod +x /tmp/chrome-linux/chrome-linux64/chrome && "
            "mv /tmp/chrome-linux/chrome-linux64/chrome /tmp/chrome-linux/chrome"
        ], check=True)

        logging.info("Downloading and setting up ChromeDriver...")
        subprocess.run([
            "bash", "-c",
            "curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.112/linux64/chromedriver-linux64.zip && "
            "unzip /tmp/chromedriver.zip -d /tmp && "
            "chmod +x /tmp/chromedriver-linux64/chromedriver && "
            "mv /tmp/chromedriver-linux64/chromedriver /tmp/chromedriver"
        ], check=True)

        logging.info("Chromium and ChromeDriver setup completed successfully!")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error installing Chromium/ChromeDriver: {e}")
        raise e

def get_data_using_selenium():
    """שולף נתונים מהקישור באמצעות דפדפן אמיתי (Selenium)"""
    logging.info("Launching Chromium browser...")

    chrome_options = Options()
    chrome_options.binary_location = CHROMIUM_PATH
    chrome_options.add_argument("--headless")  # **הרצת דפדפן ללא ממשק גרפי**
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # **קריטי ל-Render**
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info(f"Navigating to {URL}...")
    driver.get(URL)

    # המתנה לטעינת העמוד
    driver.implicitly_wait(10)

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
    install_chromium()  # **מוריד את Chromium ו-ChromeDriver לפני הפעלת השרת**
    app.run(host="0.0.0.0", port=8080)
