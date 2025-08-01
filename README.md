# YouTube to MP3 Downloader 🎵

A powerful Python script to download YouTube videos and convert them to high-quality MP3 format using `yt-dlp` and FFmpeg.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

## ✨ Features

- 🎵 Download single YouTube videos as MP3
- 📋 Download entire playlists as MP3
- 🎧 Customizable audio quality (64, 128, 192, 256, 320 kbps)
- 📊 Get video information without downloading
- 📁 Automatic file organization
- 🔄 Batch download from URL lists
- ⚡ Fast and reliable downloads
- 🛡️ Error handling and retry mechanisms
- 🌐 Cross-platform compatibility

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- FFmpeg (for audio conversion)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/youtube-to-mp3-downloader.git
   cd youtube-to-mp3-downloader
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install FFmpeg:**
   - **Windows**: Run `install_ffmpeg.bat` or download from [FFmpeg website](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

## 📖 Usage

### Basic Examples

**Download a single video:**
```bash
python youtube_to_mp3.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**High quality download:**
```bash
python youtube_to_mp3.py -q 320 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download to specific folder:**
```bash
python youtube_to_mp3.py -o "my_music" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Advanced Features

**Download entire playlist:**
```bash
python youtube_to_mp3.py -p "https://www.youtube.com/playlist?list=PLexampleplaylist"
```

**Batch download from file:**
```bash
python youtube_to_mp3.py -f urls_to_download.txt -o "Downloaded_Songs" -q 192
```

**Get video information:**
```bash
python youtube_to_mp3.py -i "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `downloads` |
| `-q, --quality` | Audio quality (64, 128, 192, 256, 320 kbps) | `192` |
| `-p, --playlist` | Download entire playlist | `False` |
| `-i, --info` | Show video info without downloading | `False` |
| `-f, --file` | Download URLs from text file | `None` |
| `-h, --help` | Show help message | - |

## 📁 Project Structure

```
youtube-to-mp3-downloader/
├── youtube_to_mp3.py          # Main script
├── convert_webm_to_mp3.py     # WebM to MP3 converter
├── requirements.txt           # Python dependencies
├── urls_to_download.txt       # Sample URL list
├── download.bat               # Windows batch script
├── download_all.bat           # Batch download script
├── install_ffmpeg.bat         # FFmpeg installer (Windows)
├── README.md                  # Documentation
└── .gitignore                 # Git ignore rules
```

## 🎵 Audio Quality Settings

| Quality | Bitrate | Use Case |
|---------|---------|----------|
| 64 kbps | Low | Voice recordings, podcasts |
| 128 kbps | Standard | General listening |
| 192 kbps | Good | Recommended default |
| 256 kbps | High | High-quality music |
| 320 kbps | Maximum | Audiophile quality |

## 🔧 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Install FFmpeg and ensure it's in your system PATH
   - On Windows, run `install_ffmpeg.bat`

2. **"Permission denied"**
   - Run terminal as administrator (Windows)
   - Check file permissions (Linux/macOS)

3. **"Network error"**
   - Check internet connection
   - Try again later (YouTube rate limiting)

4. **"Age-restricted content"**
   - Some videos cannot be downloaded due to restrictions

### Error Messages

- `❌ Error downloading video`: Check URL validity and video availability
- `❌ Please provide a valid YouTube URL`: Ensure URL contains 'youtube.com' or 'youtu.be'
- `❌ FFmpeg not found`: Install FFmpeg or provide correct path

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚖️ Legal Notice

This tool is for personal use only. Please respect:
- YouTube's Terms of Service
- Copyright laws and regulations
- Content creators' rights

Only download content you have permission to download.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing
- Python community for excellent libraries

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review existing issues before creating new ones

---

**⭐ Star this repository if you found it helpful!**
