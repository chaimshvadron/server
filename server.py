from flask import Flask, request, jsonify
import cloudscraper

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy Server is Running"

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    scraper = cloudscraper.create_scraper()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = scraper.get(url, headers=headers, timeout=10)
        return response.text, response.status_code
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
