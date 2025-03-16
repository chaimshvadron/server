from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

URL = "https://aoklivestrim.com/wp-json/purim/v1/display"

def get_data_using_selenium():
    """שולף נתונים מהקישור באמצעות דפדפן אמיתי (Selenium)"""
    logging.info("Launching Chrome browser...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # הפעלת דפדפן ללא ממשק גרפי
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
