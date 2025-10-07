## أداة تحميل الفيديوهات (YouTube والمزيد)

تطبيق Flask بسيط يدعم التحميل من منصات متعددة عبر yt-dlp: YouTube, Vimeo, Facebook, Twitter/X, Instagram, TikTok, SoundCloud وغيرها.

### المتطلبات
- Python 3.9+
- yt-dlp
- ffmpeg (لتحويل الصوت/الفيديو واقتصاصه)

### التثبيت
1. إنشاء بيئة افتراضية (اختياري)
2. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```
3. تأكد من تثبيت ffmpeg وإضافته لمسار النظام.

### التشغيل
```bash
python app.py
```
ثم افتح المتصفح على `http://127.0.0.1:5000`.

### المزايا
- جلب معلومات الفيديو وعرض الجودات (فيديو+صوت، فيديو فقط، صوت فقط)
- بحث يوتيوب وعرض النتائج
- معلومات قوائم التشغيل مع تحميل فردي أو متعدد
- تحويل إلى MP3 بجودات مختلفة
- تقطيع الفيديو عبر ffmpeg
- تحميل الترجمات بصيغة SRT
- شريط تقدم وتتبع التحميلات
- دعم منصات متعددة تلقائياً عبر yt-dlp

### منصات مدعومة
يعتمد الدعم على yt-dlp ويغطي عشرات المواقع. بعض المنصات قد تتطلب تسجيل دخول أو تكون مقيّدة جغرافياً.

### معلومات المطوّر
- الاسم: khalil agourram
- البريد: khalil.akram307@gmail.com
- Facebook: [الملف](https://web.facebook.com/khalil.akram.584342?locale=ar_AR)
- X: [الملف](https://x.com/Khalil1081506)
- Instagram: [الملف](https://www.instagram.com/kx_root/)

### الترخيص
للاستخدام الشخصي/التعليمي. احترام شروط كل منصة وحقوق النشر.
# Advanced YouTube Downloader 🎬

A sophisticated web application for downloading YouTube videos in multiple qualities with a beautiful Arabic interface and advanced features.

## ✨ Features

### 🎯 **Download Options**
- **Multiple Quality Downloads**: Video+Audio, Video Only, Audio Only
- **Playlist Support**: Download entire YouTube playlists
- **Batch Download**: Download multiple videos simultaneously
- **Quality Preview**: See available formats before downloading
- **YouTube Search**: Search and download directly from YouTube
- **Audio Conversion**: Convert videos to MP3 with high quality
- **Video Trimming**: Cut videos by time segments
- **Subtitle Download**: Download subtitles in multiple languages

### 🎨 **User Experience**
- **Dark/Light Mode**: With automatic preference saving
- **Responsive Design**: Works perfectly on all devices
- **Full Arabic Interface**: Complete RTL support with Arabic fonts
- **Real-time Progress**: Live download progress tracking
- **Smart Notifications**: Download completion alerts

### ⚡ **Advanced Features**
- **Download History**: Track all your downloads with details
- **Advanced Settings**: Customize download behavior
- **Settings Import/Export**: Backup and restore your preferences
- **Concurrent Downloads**: Multiple simultaneous downloads
- **Error Recovery**: Robust error handling and recovery

### 🛡️ **Security & Performance**
- **Safe File Handling**: Automatic filename sanitization
- **Input Validation**: Secure URL and parameter validation
- **Memory Efficient**: Optimized for large file downloads
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 🛠️ Requirements

- Python 3.7 or higher
- yt-dlp (automatically installed)
- Modern web browser

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/youtube_downloader.git
cd youtube_downloader
```

2. **Create virtual environment (optional but recommended):**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install yt-dlp:**
```bash
pip install yt-dlp
```

## 🚀 Running the Application

```bash
python app.py
```

Then open your browser and go to: `http://localhost:5000`

## 📖 How to Use

### 🎬 Single Video Download
1. **Go to "فيديو واحد" tab**
2. **Paste YouTube URL** in the input field
3. **Click "جلب معلومات الفيديو" (Fetch Video Info)** to see available options
4. **Choose appropriate quality** from three categories:
   - 🎬 **Video + Audio**: For normal viewing and listening
   - 🖼️ **Video Only**: High quality for editing (no audio)
   - 🎵 **Audio Only**: For audio-only downloads
5. **Click the download button** for your preferred option

### 📋 Playlist Download
1. **Go to "قائمة تشغيل" tab**
2. **Paste playlist URL** (e.g., `https://www.youtube.com/playlist?list=...`)
3. **Click "جلب معلومات قائمة التشغيل"** to load all videos
4. **Choose download option**:
   - Download individual videos
   - Download entire playlist at once
5. **Monitor progress** in the active downloads section

### 📦 Batch Download
1. **Go to "تحميل متعدد" tab**
2. **Paste multiple URLs** (one per line)
3. **Click "جلب معلومات جميع الفيديوهات"**
4. **Select quality** and start batch download
5. **Track progress** with real-time updates

### ⚙️ Advanced Settings
1. **Go to "الإعدادات" tab**
2. **Configure download preferences**:
   - Concurrent downloads limit
   - Default quality selection
   - Download path
   - User agent and proxy settings
3. **Save settings** or export/import configuration

### 🔍 YouTube Search
1. **Go to "بحث يوتيوب" tab**
2. **Enter search query** in Arabic or English
3. **Select number of results** (5-50)
4. **Click "بحث"** to search YouTube
5. **Choose videos** to download directly

### 🛠️ Advanced Tools
1. **Go to "أدوات متقدمة" tab**
2. **Audio Conversion**: Convert any video to MP3
3. **Video Trimming**: Cut videos by time (start/end)
4. **Subtitle Download**: Get subtitles in any language
5. **Quality Selection**: Choose MP3 quality (128k-320k)

## 🎨 Advanced Features

### 🌙 Dark Mode
- Click the 🌙/☀️ button in the top-left corner
- Your preference is automatically saved
- Smooth transitions between themes

### 📊 Progress Tracking
- **Real-time Progress Bars**: See download progress in real-time
- **Active Downloads Monitor**: Track multiple downloads simultaneously
- **Completion Notifications**: Get notified when downloads finish
- **Error Handling**: Automatic retry and error reporting

### 📋 Download Management
- **Download History**: View all previous downloads with details
- **Clear History**: Remove old download records
- **File Size Tracking**: Monitor storage usage
- **Timestamp Records**: Track when downloads were completed

### ⚙️ Smart Settings
- **Quality Categories**:
  - **Video + Audio**: MP4, WebM in various qualities
  - **Video Only**: Very high quality for professional editing
  - **Audio Only**: MP3, M4A, WebM in different sizes
- **Automatic Quality Sorting**: Best to lowest quality
- **File Size Display**: Shows approximate download size
- **Format Information**: Displays container format and codecs
- **Arabic Filename Support**: Properly handles Arabic characters

### 🔧 Configuration Options
- **Concurrent Downloads**: Control how many downloads run simultaneously
- **Default Quality**: Set preferred download quality
- **Download Path**: Customize where files are saved
- **Proxy Support**: Configure proxy settings for restricted networks
- **User Agent**: Customize browser identification
- **Settings Backup**: Export/import your configuration

### 🔍 Search & Discovery
- **Direct YouTube Search**: Search YouTube without leaving the app
- **Smart Results**: Get video thumbnails, duration, and metadata
- **Quick Download**: Download search results with one click
- **Result Filtering**: Choose number of search results (5-50)

### 🎵 Audio & Video Tools
- **High-Quality MP3**: Convert videos to MP3 (128k-320k)
- **Video Trimming**: Cut videos by specific time ranges
- **Multiple Formats**: Support for various audio/video formats
- **Batch Processing**: Process multiple files simultaneously

### 📝 Subtitle Features
- **Multi-Language Support**: Download subtitles in any language
- **Automatic Detection**: Find available subtitles automatically
- **SRT Format**: Standard subtitle format compatibility
- **Manual Selection**: Choose specific subtitle languages

## 📁 Project Structure

```
youtube_downloader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main web page
└── static/
    └── css/
        └── style.css     # Styling and themes
```

## 🔧 Customization

You can modify colors and appearance in `static/css/style.css`:

```css
:root {
    --primary-color: #d90429;    /* Primary color */
    --bg-color: #f0f2f5;        /* Background color */
    --text-color: #333;          /* Text color */
}
```

## ⚠️ Important Notes

- Ensure you have a stable internet connection
- Some videos may be protected by copyright
- Use the tool responsibly and respect creators' rights
- This tool is for personal and educational use only

## 🐛 Troubleshooting

### Quick Fix for "Server Error"
If you see "حدث خطأ غير متوقع في السيرفر" (Unexpected server error):

1. **Install/Update yt-dlp:**
```bash
pip install --upgrade yt-dlp
```

2. **Run the diagnostic tool:**
```bash
python test_connection.py
```

3. **Check app health from interface:**
   - Go to "التاريخ" (History) tab
   - Click "فحص التطبيق" (Check App)

### "yt-dlp not found" Error
```bash
pip install --upgrade yt-dlp
```

### Download Errors
- Verify the YouTube URL is correct
- Try a different video URL
- Check your internet connection
- Ensure yt-dlp is up to date

### Arabic Filename Issues
- The application automatically sanitizes filenames
- Special characters are replaced with safe alternatives
- UTF-8 encoding is properly handled

### Port Already in Use
```bash
# Kill process using port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or change port in app.py
app.run(debug=True, port=5001)
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📊 Supported Formats

| Type | Formats | Use Case |
|------|---------|----------|
| Video+Audio | MP4, WebM, 3GP | Normal viewing |
| Video Only | MP4, WebM | Professional editing |
| Audio Only | MP3, M4A, WebM | Music listening |

## 🔒 Security Features

- **Input Validation**: All URLs are validated
- **Filename Sanitization**: Prevents path traversal attacks
- **Error Handling**: Graceful error management
- **Safe Downloads**: Proper MIME type handling

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

We welcome contributions! You can:
- Report bugs and issues
- Suggest new features
- Improve the codebase
- Enhance translations
- Improve documentation

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/youtube_downloader.git
cd youtube_downloader

# Install development dependencies
pip install -r requirements.txt

# Make your changes and test
python app.py
```

## 🌟 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Icons and emojis for better UX
- Arabic font support with Google Fonts

---

**Happy Downloading! 🎉**
