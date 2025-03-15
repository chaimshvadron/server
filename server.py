from flask import Flask, jsonify
import cloudscraper
import logging
import time

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

URL = "https://aoklivestrim.com/wp-json/purim/v1/display"

@app.route('/')
def home():
    return "Proxy Server is Running"

@app.route('/proxy', methods=['GET'])
def proxy():
    logging.info(f"Fetching data from URL: {URL}")

    # יצירת Scraper שמדמה דפדפן אמיתי
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        delay=10
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://aoklivestrim.com/"
    }

    try:
        logging.info("Sending initial request to retrieve cookies...")
        session = scraper.get(URL, headers=headers, timeout=15)
        logging.info(f"Initial request status: {session.status_code}")

        if session.status_code != 200:
            logging.warning(f"Unexpected status code {session.status_code}, possible Cloudflare challenge")

        # אם התגובה נראית כמו HTML, זה אומר שהחסימה עדיין קיימת
        if "<html" in session.text.lower():
            logging.error("Cloudflare challenge detected, trying again after delay...")
            time.sleep(10)  # המתנה כדי לדמות משתמש אמיתי
            session = scraper.get(URL, headers=headers, timeout=15)

        cookies = session.cookies.get_dict()
        logging.info(f"Retrieved cookies: {cookies}")

        logging.info("Sending request with cookies...")
        response = scraper.get(URL, headers=headers, cookies=cookies, timeout=15)
        logging.info(f"Final response status: {response.status_code}")

        # אם שוב התגובה היא HTML, זה אומר שעדיין יש בעיית חסימה
        if "<html" in response.text.lower():
            logging.error("Cloudflare is still blocking the request. Consider using Puppeteer or another bypass method.")
            return "Cloudflare is still blocking the request", 403

        return response.text, response.status_code
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
