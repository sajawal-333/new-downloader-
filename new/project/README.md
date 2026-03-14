# Multi-Platform Video Downloader

A Flask-based video downloader that supports YouTube, Instagram, TikTok, and more via `yt-dlp`. It includes background processing to prevent server freezing, quality selection, MP3 conversion using FFmpeg, and an auto-deleting cleanup loop for downloaded files.

## Local Deployment

1. **Prerequisites**: Make sure you have Python 3 installed, as well as `ffmpeg` installed on your system path (needed for multiplexing video/audio and MP3 conversion).
2. **Install Dependencies**:
   If `pip` is not recognized, explicitly use the python module:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   python app.py
   ```
4. Access the web interface at `http://127.0.0.1:5000`.

## Railway Deployment

This project is fully ready to be deployed on Railway. We have included two crucial files for this:
- `Procfile`: Tells Railway exactly how to start the app using `gunicorn`.
- `Aptfile`: Tells Railway to install `ffmpeg` into the linux container so audio extraction works.

1. Create a new project on [Railway.app](https://railway.app/).
2. Select **Deploy from GitHub repo** and connect it to your Git repository containing this project.
   *(Alternatively, you can use the Railway CLI to `railway up` directly from the folder).*
3. Railway will automatically detect the Python environment, install dependencies, install `ffmpeg` via the Aptfile, and start the app using the command in the `Procfile`.
