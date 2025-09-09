from flask import Flask, render_template, request, jsonify, Response
import subprocess
import json
import re
import os
from urllib.parse import quote

app = Flask(__name__)

def sanitize_filename(title):
    """
    يزيل الأحرف غير الصالحة من العنوان ليكون اسم ملف صالح.
    """
    return re.sub(r'[\\/*?:"<>|]', "", title)

@app.route('/')
def index():
    """
    يعرض الصفحة الرئيسية للتطبيق.
    """
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    """
    يجلب معلومات الفيديو ويفصلها إلى فئات مختلفة.
    """
    url = request.json['url']
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط صالح.'}), 400

    try:
        command = ['yt-dlp', '--dump-json', '--no-warnings', url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        video_data = json.loads(result.stdout)

        video_info = {
            'title': video_data.get('title', 'بدون عنوان'),
            'thumbnail_url': video_data.get('thumbnail'),
            'duration': f"{int(video_data.get('duration', 0) // 60)}:{int(video_data.get('duration', 0) % 60):02d}",
        }

        # --- تقسيم الجودات إلى فئات ---
        video_audio_streams = [] # فيديو + صوت
        video_only_streams = []  # فيديو فقط (جودة عالية)
        audio_only_streams = []  # صوت فقط

        for f in video_data.get('formats', []):
            filesize = f.get('filesize') or f.get('filesize_approx')
            stream_info = {
                'itag': f['format_id'],
                'resolution': f.get('format_note', f.get('resolution', 'N/A')),
                'filesize': f'{filesize / 1024 / 1024:.2f} MB' if filesize else 'غير معروف',
                'ext': f.get('ext'),
                'fps': f.get('fps'),
                'vcodec': f.get('vcodec'),
                'acodec': f.get('acodec')
            }

            # تصنيف الجودات
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                video_audio_streams.append(stream_info)
            elif f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                video_only_streams.append(stream_info)
            elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                audio_only_streams.append(stream_info)

        # ترتيب الجودات من الأعلى للأقل
        video_audio_streams = sorted(video_audio_streams, key=lambda x: int(re.sub(r'\D', '', x['resolution'].split('p')[0])), reverse=True)
        video_only_streams = sorted(video_only_streams, key=lambda x: (int(re.sub(r'\D', '', x['resolution'].split('p')[0])), x.get('fps', 0)), reverse=True)
        audio_only_streams = sorted(audio_only_streams, key=lambda x: x.get('abr', 0), reverse=True)

        return jsonify({
            'video_info': video_info,
            'streams': {
                'video_audio': video_audio_streams,
                'video_only': video_only_streams,
                'audio_only': audio_only_streams
            }
        })

    except subprocess.CalledProcessError as e:
        print(f"Error calling yt-dlp: {e.stderr}")
        return jsonify({'error': 'فشل في جلب معلومات الفيديو. تأكد من أن الرابط صحيح.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'حدث خطأ غير متوقع في السيرفر.'}), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    itag = request.args.get('itag')
    title = request.args.get('title', 'video')

    if not url or not itag:
        return "معلمات ناقصة!", 400
    
    try:
        filename = sanitize_filename(title)
        
        command_get_ext = ['yt-dlp', '--print', '%(ext)s', '-f', itag, url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        ext_result = subprocess.run(command_get_ext, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        file_extension = ext_result.stdout.strip()

        # إذا طلب المستخدم صوت فقط، يمكننا تسمية الملف MP3 لتسهيل الأمر
        # yt-dlp لا يقوم بالتحويل هنا، فقط يبث البيانات الخام
        is_audio_request = request.args.get('is_audio') == 'true'
        download_extension = "mp3" if is_audio_request else file_extension
        download_name = f"{filename}.{download_extension}"
        
        encoded_filename = quote(download_name)
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        command = ['yt-dlp', '-f', itag, '-o', '-', url]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        return Response(iter(lambda: process.stdout.read(8192), b''),
                        mimetype='application/octet-stream',
                        headers=headers)

    except Exception as e:
        print(f"Download error: {e}")
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)

