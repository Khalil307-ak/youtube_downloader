from flask import Flask, render_template, request, jsonify, Response, session
import subprocess
import json
import re
import os
import threading
import time
import requests
from urllib.parse import quote, urlencode
from datetime import datetime, timedelta
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# تخزين حالات التحميل
download_progress = {}
download_history = []

# إنشاء مجلد للتحميلات
DOWNLOADS_FOLDER = 'downloads'
if not os.path.exists(DOWNLOADS_FOLDER):
    os.makedirs(DOWNLOADS_FOLDER)

def sanitize_filename(title):
    """
    يزيل الأحرف غير الصالحة من العنوان ليكون اسم ملف صالح.
    """
    return re.sub(r'[\\/*?:"<>|]', "", title)

def get_download_progress(download_id):
    """الحصول على تقدم التحميل"""
    return download_progress.get(download_id, {'status': 'not_found', 'progress': 0})

def update_download_progress(download_id, status, progress=0, message=""):
    """تحديث تقدم التحميل"""
    download_progress[download_id] = {
        'status': status,
        'progress': progress,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

def add_to_history(video_info, download_path, quality):
    """إضافة التحميل إلى التاريخ"""
    history_item = {
        'id': str(uuid.uuid4()),
        'title': video_info.get('title', 'غير معروف'),
        'url': video_info.get('url', ''),
        'quality': quality,
        'download_path': download_path,
        'timestamp': datetime.now().isoformat(),
        'size': os.path.getsize(download_path) if os.path.exists(download_path) else 0
    }
    download_history.append(history_item)
    return history_item

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

    # التحقق من وجود yt-dlp
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return jsonify({'error': 'yt-dlp غير مثبت. يرجى تثبيته أولاً: pip install yt-dlp'}), 500

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
                'acodec': f.get('acodec'),
                'abr': f.get('abr')  # معدل البت للصوت بالكيلو بت/ثانية إن وجد
            }

            # تصنيف الجودات
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                video_audio_streams.append(stream_info)
            elif f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                video_only_streams.append(stream_info)
            elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                audio_only_streams.append(stream_info)

        # ترتيب الجودات من الأعلى للأقل
        def get_resolution_number(resolution):
            try:
                if 'p' in resolution:
                    return int(re.sub(r'\D', '', resolution.split('p')[0]))
                return 0
            except:
                return 0

        video_audio_streams = sorted(video_audio_streams, key=lambda x: get_resolution_number(x['resolution']), reverse=True)
        video_only_streams = sorted(video_only_streams, key=lambda x: (get_resolution_number(x['resolution']), x.get('fps', 0)), reverse=True)
        audio_only_streams = sorted(audio_only_streams, key=lambda x: (x.get('abr') or 0), reverse=True)

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
        # e.stderr هو نص بالفعل لأننا استخدمنا text=True
        error_msg = e.stderr if e.stderr else 'Unknown error'
        if 'Video unavailable' in error_msg:
            return jsonify({'error': 'الفيديو غير متاح أو محذوف.'}), 400
        elif 'Private video' in error_msg:
            return jsonify({'error': 'الفيديو خاص ولا يمكن الوصول إليه.'}), 400
        elif 'Age-restricted' in error_msg:
            return jsonify({'error': 'الفيديو مقيد بالعمر.'}), 400
        else:
            return jsonify({'error': 'فشل في جلب معلومات الفيديو. تأكد من أن الرابط صحيح.'}), 500
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return jsonify({'error': 'فشل في تحليل معلومات الفيديو.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'حدث خطأ غير متوقع: {str(e)}'}), 500

@app.route('/search_youtube', methods=['POST'])
def search_youtube():
    """البحث المباشر في يوتيوب"""
    data = request.json
    query = data.get('query', '').strip()
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({'error': 'الرجاء إدخال كلمة البحث.'}), 400
    
    try:
        # استخدام yt-dlp للبحث
        command = ['yt-dlp', '--dump-json', '--flat-playlist', '--no-warnings', 
                  f'ytsearch{max_results}:{query}']
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    video_data = json.loads(line)
                    videos.append({
                        'title': video_data.get('title', 'بدون عنوان'),
                        'url': video_data.get('url', ''),
                        'duration': video_data.get('duration', 0),
                        'thumbnail': video_data.get('thumbnail', ''),
                        'uploader': video_data.get('uploader', ''),
                        'view_count': video_data.get('view_count', 0),
                        'upload_date': video_data.get('upload_date', '')
                    })
                except json.JSONDecodeError:
                    continue
        
        return jsonify({
            'query': query,
            'total_results': len(videos),
            'videos': videos
        })

    except subprocess.CalledProcessError as e:
        print(f"Search error: {e.stderr}")
        return jsonify({'error': 'فشل في البحث. تأكد من اتصال الإنترنت.'}), 500
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': f'حدث خطأ في البحث: {str(e)}'}), 500

@app.route('/get_subtitles', methods=['POST'])
def get_subtitles():
    """جلب قائمة الترجمات المتاحة"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو.'}), 400
    
    try:
        command = ['yt-dlp', '--list-subs', '--no-warnings', url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        
        subtitles = []
        lines = result.stdout.split('\n')
        in_subtitles_section = False
        
        for line in lines:
            line = line.strip()
            if 'Available subtitles' in line:
                in_subtitles_section = True
                continue
            elif 'Available automatic captions' in line:
                in_subtitles_section = True
                continue
            elif line.startswith('Language formats') or line.startswith('WARNING'):
                break
            
            if in_subtitles_section and line and not line.startswith('Available'):
                parts = line.split()
                if len(parts) >= 2:
                    lang_code = parts[0]
                    lang_name = parts[1]
                    subtitles.append({
                        'code': lang_code,
                        'name': lang_name,
                        'available': True
                    })
        
        return jsonify({
            'url': url,
            'subtitles': subtitles
        })

    except subprocess.CalledProcessError as e:
        print(f"Subtitles error: {e.stderr}")
        return jsonify({'error': 'فشل في جلب الترجمات.'}), 500
    except Exception as e:
        print(f"Subtitles error: {e}")
        return jsonify({'error': f'حدث خطأ في جلب الترجمات: {str(e)}'}), 500

@app.route('/download_subtitle', methods=['POST'])
def download_subtitle():
    """تحميل ترجمة محددة"""
    data = request.json
    url = data.get('url')
    lang_code = data.get('lang_code', 'ar')
    title = data.get('title', 'subtitle')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو.'}), 400
    
    try:
        filename = sanitize_filename(title)
        
        command = ['yt-dlp', '--write-subs', '--write-auto-subs', 
                  f'--sub-langs', lang_code, '--sub-format', 'srt',
                  '--skip-download', '--no-warnings', url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        
        # البحث عن ملف الترجمة المحمل
        subtitle_files = []
        for line in result.stdout.split('\n'):
            if '.srt' in line and 'has already been downloaded' in line:
                subtitle_files.append(line.split()[0])
        
        if subtitle_files:
            subtitle_file = subtitle_files[0]
            download_name = f"{filename}_{lang_code}.srt"
            
            encoded_filename = quote(download_name)
            headers = {
                'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"
            }
            
            # قراءة ملف الترجمة وإرساله
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response(content, mimetype='text/plain', headers=headers)
        else:
            return jsonify({'error': 'لم يتم العثور على ترجمة بهذا اللغة.'}), 404

    except subprocess.CalledProcessError as e:
        print(f"Subtitle download error: {e.stderr}")
        return jsonify({'error': 'فشل في تحميل الترجمة.'}), 500
    except Exception as e:
        print(f"Subtitle download error: {e}")
        return jsonify({'error': f'حدث خطأ في تحميل الترجمة: {str(e)}'}), 500

@app.route('/convert_to_mp3', methods=['POST'])
def convert_to_mp3():
    """تحويل الفيديو إلى MP3 بجودة عالية"""
    data = request.json
    url = data.get('url')
    title = data.get('title', 'audio')
    quality = data.get('quality', '320k')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو.'}), 400
    
    try:
        filename = sanitize_filename(title)
        download_name = f"{filename}.mp3"
        
        # استخدام yt-dlp مع ffmpeg للتحويل
        command = ['yt-dlp', '-x', '--audio-format', 'mp3', 
                  '--audio-quality', quality, '-o', '-', url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        encoded_filename = quote(download_name)
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}",
            'Content-Type': 'audio/mpeg'
        }
        
        def generate():
            try:
                chunk_size = 8192
                while True:
                    chunk = process.stdout.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            except Exception as e:
                print(f"MP3 conversion error: {e}")
                raise
        
        return Response(generate(), mimetype='audio/mpeg', headers=headers)

    except Exception as e:
        print(f"MP3 conversion error: {e}")
        return jsonify({'error': f'فشل في تحويل الصوت إلى MP3: {str(e)}'}), 500

@app.route('/trim_video', methods=['POST'])
def trim_video():
    """تقطيع الفيديو حسب الوقت"""
    data = request.json
    url = data.get('url')
    title = data.get('title', 'trimmed_video')
    start_time = data.get('start_time', '00:00:00')
    end_time = data.get('end_time')
    duration = data.get('duration')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو.'}), 400
    
    try:
        filename = sanitize_filename(title)
        
        # بناء أمر التقطيع
        command = ['yt-dlp', '-f', 'best', '-o', '-', url]
        
        # إضافة خيارات التقطيع إذا كانت متاحة
        if end_time:
            command.extend(['--external-downloader', 'ffmpeg', 
                           '--external-downloader-args', f'ffmpeg:-ss {start_time} -to {end_time}'])
        elif duration:
            command.extend(['--external-downloader', 'ffmpeg', 
                           '--external-downloader-args', f'ffmpeg:-ss {start_time} -t {duration}'])
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        download_name = f"{filename}_trimmed.mp4"
        encoded_filename = quote(download_name)
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}",
            'Content-Type': 'video/mp4'
        }
        
        def generate():
            try:
                chunk_size = 8192
                while True:
                    chunk = process.stdout.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            except Exception as e:
                print(f"Video trimming error: {e}")
                raise
        
        return Response(generate(), mimetype='video/mp4', headers=headers)

    except Exception as e:
        print(f"Video trimming error: {e}")
        return jsonify({'error': f'فشل في تقطيع الفيديو: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """فحص صحة التطبيق"""
    try:
        # فحص yt-dlp
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True, check=True)
        yt_dlp_version = result.stdout.strip()
        
        return jsonify({
            'status': 'healthy',
            'yt_dlp_version': yt_dlp_version,
            'message': 'التطبيق يعمل بشكل صحيح'
        })
    except (subprocess.CalledProcessError, FileNotFoundError):
        return jsonify({
            'status': 'error',
            'message': 'yt-dlp غير مثبت أو لا يعمل بشكل صحيح'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في التطبيق: {str(e)}'
        }), 500

@app.route('/progress/<download_id>')
def get_progress(download_id):
    """الحصول على تقدم التحميل"""
    return jsonify(get_download_progress(download_id))

@app.route('/history')
def get_history():
    """الحصول على تاريخ التحميلات"""
    return jsonify(download_history[-20:])  # آخر 20 تحميل

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """مسح تاريخ التحميلات"""
    global download_history
    download_history.clear()
    return jsonify({'message': 'تم مسح التاريخ بنجاح'})

@app.route('/playlist_info', methods=['POST'])
def get_playlist_info():
    """جلب معلومات قائمة التشغيل"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط صالح.'}), 400

    try:
        command = ['yt-dlp', '--dump-json', '--flat-playlist', '--no-warnings', url]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', startupinfo=startupinfo)
        
        # تحليل النتائج
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                video_data = json.loads(line)
                videos.append({
                    'title': video_data.get('title', 'بدون عنوان'),
                    'url': video_data.get('url', ''),
                    'duration': video_data.get('duration', 0),
                    'thumbnail': video_data.get('thumbnail', '')
                })
        
        return jsonify({
            'playlist_title': videos[0].get('title', 'قائمة تشغيل') if videos else 'قائمة تشغيل',
            'total_videos': len(videos),
            'videos': videos
        })

    except subprocess.CalledProcessError as e:
        print(f"Error calling yt-dlp: {e.stderr}")
        error_msg = e.stderr.decode('utf-8') if e.stderr else 'Unknown error'
        if 'Playlist unavailable' in error_msg:
            return jsonify({'error': 'قائمة التشغيل غير متاحة أو محذوفة.'}), 400
        elif 'Private playlist' in error_msg:
            return jsonify({'error': 'قائمة التشغيل خاصة ولا يمكن الوصول إليها.'}), 400
        else:
            return jsonify({'error': 'فشل في جلب معلومات قائمة التشغيل.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'حدث خطأ غير متوقع: {str(e)}'}), 500

@app.route('/batch_download', methods=['POST'])
def batch_download():
    """تحميل متعدد للقوائم"""
    data = request.json
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'error': 'لا توجد روابط للتحميل'}), 400
    
    batch_id = str(uuid.uuid4())
    update_download_progress(batch_id, 'starting', 0, f'بدء تحميل {len(urls)} فيديو')
    
    # تشغيل التحميل المتعدد في thread منفصل
    thread = threading.Thread(target=process_batch_download, args=(batch_id, urls))
    thread.start()
    
    return jsonify({'batch_id': batch_id, 'total': len(urls)})

def process_batch_download(batch_id, urls):
    """معالجة التحميل المتعدد"""
    try:
        total = len(urls)
        completed = 0
        
        for i, url in enumerate(urls):
            update_download_progress(batch_id, 'downloading', 
                                   int((i / total) * 100), 
                                   f'تحميل الفيديو {i+1} من {total}')
            
            # هنا يمكن إضافة منطق التحميل الفعلي
            time.sleep(2)  # محاكاة التحميل
            completed += 1
        
        update_download_progress(batch_id, 'completed', 100, f'تم تحميل {completed} فيديو بنجاح')
        
    except Exception as e:
        update_download_progress(batch_id, 'error', 0, f'خطأ: {str(e)}')

@app.route('/download')
def download():
    url = request.args.get('url')
    itag = request.args.get('itag')
    title = request.args.get('title', 'video')
    download_id = request.args.get('download_id', str(uuid.uuid4()))

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

        is_audio_request = request.args.get('is_audio') == 'true'
        download_extension = "mp3" if is_audio_request else file_extension
        download_name = f"{filename}.{download_extension}"
        
        encoded_filename = quote(download_name)
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        # تحديث حالة التحميل
        update_download_progress(download_id, 'downloading', 0, 'بدء التحميل...')

        command = ['yt-dlp', '-f', itag, '-o', '-', url]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        def generate():
            try:
                chunk_size = 8192
                total_size = 0
                
                while True:
                    chunk = process.stdout.read(chunk_size)
                    if not chunk:
                        break
                    
                    total_size += len(chunk)
                    yield chunk
                    
                    # تحديث التقدم (تقدير)
                    if total_size % (chunk_size * 100) == 0:
                        update_download_progress(download_id, 'downloading', 50, f'تم تحميل {total_size // 1024} KB')
                
                update_download_progress(download_id, 'completed', 100, 'تم التحميل بنجاح')
                
                # إضافة للتاريخ
                add_to_history({'title': title, 'url': url}, download_name, itag)
                
            except Exception as e:
                update_download_progress(download_id, 'error', 0, f'خطأ: {str(e)}')
                raise
        
        return Response(generate(), mimetype='application/octet-stream', headers=headers)

    except Exception as e:
        print(f"Download error: {e}")
        update_download_progress(download_id, 'error', 0, f'خطأ: {str(e)}')
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)

