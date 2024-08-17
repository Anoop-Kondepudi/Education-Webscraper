from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Directory where HTML files are stored
HTML_FILES_DIRECTORY = "C:\\Users\\MCBat\\Downloads"  # Update this path

@app.route('/unlocked/<filename>')
def serve_html(filename):
    return send_from_directory(HTML_FILES_DIRECTORY, filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))