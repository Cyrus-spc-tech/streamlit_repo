import streamlit as st
import yt_dlp
import os
import tempfile
from pathlib import Path
import re

# Set page configuration
st.set_page_config(
    page_title="YT Downloader",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="auto"
)

# Title and description
st.title("📥 YouTube Video Downloader")
st.markdown("Download YouTube videos in various formats and qualities")
st.markdown("---")

def is_valid_youtube_url(url):
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return youtube_regex.match(url) is not None

def get_video_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'cookiefile': None,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls']
                }
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def download_video(url, format_choice, quality_choice):
    try:
        temp_dir = tempfile.mkdtemp()
        
        # Enhanced yt-dlp options to bypass restrictions
        base_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': False,  # Set to False for debugging
            'no_warnings': False,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': False,
            'cookiefile': None,
            # Add user agent and headers to avoid detection
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '115',
                'Connection': 'keep-alive',
            },
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web']
                }
            }
        }
        
        if format_choice == "MP4 (Video)":
            if quality_choice == "Best":
                base_opts['format'] = 'best[ext=mp4]/best'
            elif quality_choice == "720p":
                base_opts['format'] = 'best[height<=720][ext=mp4]/best[height<=720]'
            elif quality_choice == "480p":
                base_opts['format'] = 'best[height<=480][ext=mp4]/best[height<=480]'
            else:  # 360p
                base_opts['format'] = 'best[height<=360][ext=mp4]/best[height<=360]'
        else:  # MP3 (Audio)
            base_opts['format'] = 'bestaudio/best'
            base_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            ydl.download([url])
     
        files = list(Path(temp_dir).glob('*'))
        if files:
            return files[0]
        return None
        
    except yt_dlp.DownloadError as e:
        if "403" in str(e):
            st.error("❌ Access forbidden. This video may be restricted, private, or region-locked.")
            st.info("💡 Try a different video or check if the video is public.")
        elif "429" in str(e):
            st.error("❌ Too many requests. Please wait a moment and try again.")
        else:
            st.error(f"Download error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None


url = st.text_input(
    "Enter YouTube URL:",
    placeholder="https://www.youtube.com/watch?v=..."
)

if url:
    if is_valid_youtube_url(url):
        st.success("✅ Valid YouTube URL")
        
        
        with st.spinner("Getting video information..."):
            video_info = get_video_info(url)
        
        if video_info:

            col1, col2 = st.columns([1, 2])
            
            with col1:
                if 'thumbnail' in video_info:
                    st.image(video_info['thumbnail'], width=200)
            
            with col2:
                st.subheader(video_info.get('title', 'Unknown Title'))
                st.write(f"**Channel:** {video_info.get('uploader', 'Unknown')}")
                st.write(f"**Duration:** {video_info.get('duration_string', 'Unknown')}")
                st.write(f"**Views:** {video_info.get('view_count', 'Unknown'):,}" if video_info.get('view_count') else "**Views:** Unknown")
            
            st.markdown("---")

            col1, col2 = st.columns(2)
            
            with col1:
                format_choice = st.selectbox(
                    "Select Format:",
                    ["MP4 (Video)", "MP3 (Audio)"]
                )
            
            with col2:
                if format_choice == "MP4 (Video)":
                    quality_choice = st.selectbox(
                        "Select Quality:",
                        ["Best", "720p", "480p", "360p"]
                    )
                else:
                    quality_choice = st.selectbox(
                        "Select Quality:",
                        ["192 kbps"]
                    )
            
            # Download button
            if st.button("📥 Download", use_container_width=True):
                with st.spinner("Downloading... Please wait"):
                    downloaded_file = download_video(url, format_choice, quality_choice)
                
                if downloaded_file:
                    # Read file for download
                    with open(downloaded_file, 'rb') as file:
                        file_data = file.read()
                    
                    # Determine file extension
                    file_ext = downloaded_file.suffix
                    filename = f"{video_info.get('title', 'download')}{file_ext}"
                    
                    # Clean filename
                    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
                    
                    # Provide download button
                    st.download_button(
                        label=f"💾 Download {filename}",
                        data=file_data,
                        file_name=filename,
                        mime="video/mp4" if format_choice == "MP4 (Video)" else "audio/mpeg"
                    )
                    
                    st.success("✅ Download ready!")
                    
                    # Clean up temporary file
                    try:
                        os.remove(downloaded_file)
                        os.rmdir(downloaded_file.parent)
                    except:
                        pass
        else:
            st.error("❌ Could not retrieve video information. Please check the URL.")
    else:
        st.error("❌ Please enter a valid YouTube URL")

