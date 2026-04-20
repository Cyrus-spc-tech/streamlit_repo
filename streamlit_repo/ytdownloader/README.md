# 📥 YouTube Video Downloader

A simple and user-friendly YouTube video downloader built with Streamlit that allows you to download videos in various formats and qualities.

## 🌐 Live Demo

**Access the app directly at: [yt34downloader.streamlit.app](https://yt34downloader.streamlit.app)**

No installation required! Just visit the link and start downloading.

## ✨ Features

- **Easy to Use**: Simple web interface - just paste a YouTube URL
- **Multiple Formats**: Download as MP4 (video) or MP3 (audio only)
- **Quality Options**: Choose from Best, 720p, 480p, or 360p for videos
- **Video Information**: Preview thumbnail, title, channel, duration, and view count
- **Direct Download**: Download files directly to your device
- **Error Handling**: Clear error messages and troubleshooting tips

## 🚀 How to Use

### Online (Recommended)
1. Visit [yt34downloader.streamlit.app](https://yt34downloader.streamlit.app)
2. Paste a YouTube URL in the input field
3. Select your preferred format (MP4 or MP3)
4. Choose quality settings
5. Click "Download" and save the file

### Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd ytdownloader

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📋 Requirements

- Python 3.7+
- Streamlit
- yt-dlp
- FFmpeg (for audio conversion)

## 🎯 Supported Content

### ✅ Works With:
- Public YouTube videos
- Educational content
- Creative Commons videos
- Music videos (where permitted)
- Podcasts and lectures

### ❌ May Not Work With:
- Age-restricted content
- Private or unlisted videos
- Live streams
- Region-locked content
- Copyrighted material with strict protection

## 🛠️ Troubleshooting

### Common Issues:

#### "403 Forbidden" Error
- **Cause**: Video may be restricted, private, or region-locked
- **Solution**: Try a different video or check if the video is public

#### "Unable to Download" Error
- **Cause**: Network issues or video restrictions
- **Solutions**:
  - Check your internet connection
  - Try a different quality setting
  - Wait a few minutes and try again
  - Ensure the video URL is correct

#### Audio Download Issues
- **Cause**: Missing FFmpeg
- **Solution**: Install FFmpeg on your system

### Tips for Better Success:
1. Use public, non-restricted videos
2. Try different quality options if one fails
3. Avoid downloading copyrighted content
4. Wait between downloads to avoid rate limiting

## 🔧 Technical Details

### Built With:
- **Streamlit**: Web framework for the user interface
- **yt-dlp**: Powerful YouTube downloader library
- **Python**: Backend processing

### Format Support:
- **Video**: MP4 format with various quality options
- **Audio**: MP3 format at 192 kbps

## ⚖️ Legal Notice

**Important**: Please respect copyright laws and YouTube's Terms of Service when using this tool.

- Only download content you have rights to use
- Respect creators' intellectual property
- Use downloaded content for personal use only
- Do not redistribute copyrighted material

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure you're using a valid, public YouTube URL
3. Try different quality settings
4. Verify your internet connection

## 🔄 Updates

This app is regularly updated to maintain compatibility with YouTube's changes. If you experience issues, try refreshing the page or visiting the app later.

## 📄 License

This project is for educational purposes. Please use responsibly and in accordance with applicable laws and terms of service.

---

**Ready to download? Visit [yt34downloader.streamlit.app](https://yt34downloader.streamlit.app) now!** 🎬