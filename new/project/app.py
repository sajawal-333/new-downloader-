import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from downloader_core import download_video

# Define base directory explicitly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# Base directory for downloads
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# In-memory task tracker
tasks = {}

import time

def bg_download(task_id, url, format_type, quality):
    try:
        # Step 5 fallback messages could be retrieved here if we parsed the exact downloaded format,
        # but yt-dlp handles the fallback internally based on our string.
        result = download_video(url, format_type, quality)
        if result.get('status') == 'success':
            tasks[task_id] = {
                'status': 'success',
                'filename': result['filename'],
                'title': result.get('title', 'Unknown Title')
            }
        else:
            tasks[task_id] = {
                'status': 'error',
                'message': result.get('message', 'Unknown error occurred')
            }
    except Exception as e:
        tasks[task_id] = {
            'status': 'error',
            'message': str(e)
        }

def cleanup_loop():
    while True:
        try:
            now = time.time()
            for filename in os.listdir(DOWNLOAD_DIR):
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(filepath):
                    # Check if older than 24 hours (86400 seconds)
                    if os.stat(filepath).st_mtime < now - 86400:
                        os.remove(filepath)
                        print(f"Cleaned up old file: {filename}")
        except Exception as e:
            print(f"Cleanup error: {e}")
        time.sleep(3600) # run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_download', methods=['POST'])
def start_download():
    data = request.json or request.form
    url = data.get('url')
    format_type = data.get('format', 'mp4')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'}), 400
        
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'downloading'}
    
    # Start background thread to avoid blocking Flask (Step 4 & Mistral 3)
    thread = threading.Thread(target=bg_download, args=(task_id, url, format_type, quality))
    thread.start()
    
    return jsonify({'status': 'success', 'task_id': task_id})

@app.route('/status/<task_id>')
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'}), 404
        
    return jsonify(task)

@app.route('/download/<filename>')
def download_file(filename):
    # Ensure it's safe and inside downloads directory
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
