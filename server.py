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

# **התקנת Chrome באופן אוטומטי אם הוא לא קיים**
def install_chrome():
    if not os.path.exists("/usr/bin/google-chrome"):
        logging.info("Installing Chrome...")
        subprocess.run([
            "bash", "-c",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && "
            "sudo sh -c 'echo \"deb http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list' && "
            "sudo apt update && sudo apt install -y google-chrome-stable"
        ], check=True)
        logging.info("Chrome installed successfully.")
    else:
        logging.info("Chrome is already installed.")

install_chrome()  # **הרצת ההתקנה לפני שהשרת מתחיל לפעול**

def get_data_using_selenium():
    """שולף נתונים מהקישור באמצעות דפדפן אמיתי (Selenium)"""
    logging.info("Launching Chrome browser...")

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"  # **הגדרת הנתיב ל-Chrome**
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
