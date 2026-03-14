import os
import yt_dlp

def download_video(url, format_type='mp4', quality='best'):
    # Ensure downloads directory exists in project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    # Base options for yt-dlp
    ydl_opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'restrictfilenames': True,  # Keep filenames safe
        'noplaylist': True,
        'quiet': False, # To see output during test
    }
    
    # Handle Format and Quality
    if format_type == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Step 5 logic included: map qualities to yt-dlp format strings
        # We request the best single file (video+audio) up to the specified height
        # We request the best video and audio and let yt-dlp merge them, 
        # but provide a fallback if ffmpeg is missing or formats don't exist
        ydl_opts['merge_output_format'] = 'mp4'
        if quality == '360p':
            ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
        elif quality == '720p':
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
        elif quality == '1080p':
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
        elif quality == '2160p':
            ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best'
        elif quality == 'test':
            ydl_opts['format'] = '18' # Guaranteed mp4 for small YouTube tests
        else: # 'best'
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                # extension is changed by postprocessor
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            # Use os.path.basename to just return the relative filename for Flask
            return {
                'status': 'success', 
                'file_path': filename,
                'filename': os.path.basename(filename),
                'title': info.get('title')
            }
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Requested format is not available" in error_msg:
            return {'status': 'error', 'message': "This video has no downloadable formats available (e.g. it might be a Premiere, a Live stream, or restricted)."}
        return {'status': 'error', 'message': error_msg}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    # Test requirement: Download a sample YouTube video
    sample_url = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ' # Big Buck Bunny
    print(f"Testing download for {sample_url}")
    # Using quality='test' to skip ffmpeg requirements on this local agent machine
    result = download_video(sample_url, format_type='mp4', quality='test')
    print("Result:", result)
