from flask import Flask, request, jsonify, send_file, abort
import os
import json
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
WORKS_EXCLUDE = {'index', 'works', 'contact'}

DATA_FILE = os.path.join('static', 'data.js')

@app.route('/')
def home():
    return send_file(BASE_DIR / 'index.html')


@app.route('/api/works-pages')
def works_pages():
    pages = sorted(
        p.stem for p in BASE_DIR.glob('*.html')
        if p.stem not in WORKS_EXCLUDE
    )
    return jsonify(pages)

@app.route('/<path:page>')
def serve_page(page):
    """Serve HTML pages and static files from the root directory"""
    normalized_page = page.strip('/').replace('\\', '/').rstrip('/')
    file_path = BASE_DIR / normalized_page

    if file_path.exists() and file_path.is_file():
        return send_file(file_path)

    if not normalized_page.endswith('.html'):
        html_file_path = BASE_DIR / f"{normalized_page}.html"
        if html_file_path.exists() and html_file_path.is_file():
            return send_file(html_file_path)

    abort(404)

@app.route('/submit-signup', methods=['POST'])
def submit_signup():
    data = request.get_json()
    
    # Path to your data file
    filepath = 'signups.json'

    # Read and safely parse existing JSON
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                content = f.read().strip()
                signups = json.loads(content) if content else []
            except json.JSONDecodeError:
                signups = []
    else:
        signups = []

    # Append new signup
    signups.append(data)

    # Write back to JSON file
    with open(filepath, 'w') as f:
        json.dump(signups, f, indent=4)

    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
