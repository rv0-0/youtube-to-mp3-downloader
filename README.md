# YouTube to MP3 Downloader 🎵

A powerful Python script to download YouTube videos and convert them to high-quality MP3 format using `yt-dlp` and FFmpeg.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

## ✨ Features

### 🎵 Basic Features (All Versions)
- Download single YouTube videos as MP3
- Download entire playlists as MP3
- Customizable audio quality (64, 128, 192, 256, 320 kbps)
- Get video information without downloading
- Automatic file organization
- Cross-platform compatibility

### ⚡ Advanced Features (`youtube_to_mp3_advanced.py`)
- 📥 Resume interrupted downloads automatically
- 🖼️ Download and embed thumbnails as album art
- 🏷️ Extract and apply metadata (title, artist, duration, etc.)
- 📋 Automatic playlist detection from video URLs
- ⚡ Parallel downloads for faster processing
- � Rate limiting to be respectful to servers
- 📊 Download history tracking

### 🧠 Smart Features (`youtube_to_mp3_smart.py`)
- 🔍 Intelligent duplicate detection and skipping
- 🏷️ Enhanced automatic metadata tagging
- 📁 Smart playlist organization into folders
- ⭐ Download history and favorites system
- 🔄 Auto-retry with exponential backoff
- 📊 Comprehensive statistics and reporting
- 🛡️ Thread-safe operations with file locking
- 🎯 Content-based similarity detection

## 🚀 Quick Start

### Three Versions Available

1. **`youtube_to_mp3.py`** - Basic version with core functionality
2. **`youtube_to_mp3_advanced.py`** - Advanced version with parallel downloads, resume, thumbnails
3. **`youtube_to_mp3_smart.py`** - Smart version with AI-like features, duplicate detection, auto-retry

Choose the version that best fits your needs!

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

### Basic Version (`youtube_to_mp3.py`)

**Download a single video:**
```bash
python youtube_to_mp3.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Batch download:**
```bash
python youtube_to_mp3.py -f urls_to_download.txt
```

### Advanced Version (`youtube_to_mp3_advanced.py`)

**Parallel downloads with thumbnails:**
```bash
python youtube_to_mp3_advanced.py -f urls.txt -w 5 -q 320
```

**Resume interrupted downloads:**
```bash
python youtube_to_mp3_advanced.py --resume
```

**Auto-detect playlist:**
```bash
python youtube_to_mp3_advanced.py --auto-playlist "VIDEO_URL"
```

### Smart Version (`youtube_to_mp3_smart.py`)

**Smart batch download with duplicate detection:**
```bash
python youtube_to_mp3_smart.py -f urls.txt --skip-duplicates -w 3
```

**View statistics:**
```bash
python youtube_to_mp3_smart.py --stats
```

**Add to favorites:**
```bash
python youtube_to_mp3_smart.py --add-favorite VIDEO_ID
```

### Batch Scripts

**Windows users can use the convenient batch files:**
- `download.bat` - Basic downloader
- `download_advanced.bat` - Advanced features
- `download_smart.bat` - Smart features

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
├── 🎵 Core Scripts
│   ├── youtube_to_mp3.py              # Basic downloader
│   ├── youtube_to_mp3_advanced.py     # Advanced features
│   └── youtube_to_mp3_smart.py        # Smart features with AI-like capabilities
├── 🔧 Utilities
│   ├── convert_webm_to_mp3.py         # WebM to MP3 converter
│   └── install_ffmpeg.bat             # FFmpeg installer (Windows)
├── 📋 Configuration
│   ├── config.ini                     # Basic configuration
│   ├── smart_config.ini               # Smart features configuration
│   └── requirements.txt               # Python dependencies
├── 🚀 Batch Scripts
│   ├── download.bat                   # Basic batch downloader
│   ├── download_advanced.bat          # Advanced batch downloader
│   ├── download_smart.bat             # Smart batch downloader
│   └── download_all.bat               # Batch download all URLs
├── 📄 Documentation
│   ├── README.md                      # Comprehensive documentation
│   └── LICENSE                        # MIT License
└── 📂 Runtime Directories (created automatically)
    ├── downloads/                     # Downloaded MP3 files
    ├── playlists/                     # Organized playlist folders
    ├── thumbnails/                    # Downloaded thumbnails/album art
    ├── metadata/                      # Video metadata JSON files
    └── .history/                      # Download history and statistics
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
