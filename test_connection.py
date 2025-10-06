#!/usr/bin/env python3
"""
ملف تشخيص شامل لفحص التطبيق
"""

import subprocess
import sys
import json
import requests

def test_yt_dlp():
    """فحص وجود yt-dlp"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ yt-dlp مثبت بنجاح - الإصدار: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ yt-dlp غير مثبت")
        print("💡 قم بتثبيته باستخدام: pip install yt-dlp")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في yt-dlp: {e}")
        return False

def test_ffmpeg():
    """فحص وجود ffmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        print("✅ ffmpeg متوفر - يمكن تحويل الصوت والفيديو")
        return True
    except FileNotFoundError:
        print("⚠️ ffmpeg غير مثبت - بعض الميزات قد لا تعمل")
        print("💡 قم بتثبيته من: https://ffmpeg.org/download.html")
        return False
    except subprocess.CalledProcessError:
        print("⚠️ ffmpeg لا يعمل بشكل صحيح")
        return False

def test_youtube_access():
    """فحص الوصول إلى يوتيوب"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        command = ['yt-dlp', '--dump-json', '--no-warnings', test_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        print(f"✅ الوصول إلى يوتيوب يعمل - عنوان الاختبار: {data.get('title', 'غير معروف')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ فشل في الوصول إلى يوتيوب: {e.stderr.decode('utf-8')}")
        return False
    except json.JSONDecodeError:
        print("❌ خطأ في تحليل بيانات يوتيوب")
        return False

def test_youtube_search():
    """فحص البحث في يوتيوب"""
    try:
        command = ['yt-dlp', '--dump-json', '--flat-playlist', '--no-warnings', 'ytsearch1:test']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("✅ البحث في يوتيوب يعمل بشكل صحيح")
            return True
        else:
            print("❌ البحث في يوتيوب لا يعمل")
            return False
    except subprocess.CalledProcessError:
        print("❌ فشل في اختبار البحث")
        return False

def test_internet_connection():
    """فحص اتصال الإنترنت"""
    try:
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            print("✅ اتصال الإنترنت يعمل بشكل صحيح")
            return True
        else:
            print("❌ مشكلة في اتصال الإنترنت")
            return False
    except requests.RequestException:
        print("❌ لا يوجد اتصال بالإنترنت")
        return False

def test_subtitle_support():
    """فحص دعم الترجمات"""
    try:
        # اختبار فيديو يحتوي على ترجمات
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        command = ['yt-dlp', '--list-subs', '--no-warnings', test_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if 'Available subtitles' in result.stdout or 'Available automatic captions' in result.stdout:
            print("✅ دعم الترجمات متوفر")
            return True
        else:
            print("⚠️ لا توجد ترجمات متاحة للفيديو التجريبي")
            return True  # هذا ليس خطأ
    except subprocess.CalledProcessError:
        print("⚠️ فشل في فحص دعم الترجمات")
        return False

def main():
    print("🔍 فحص شامل للتطبيق...")
    print("=" * 60)
    
    tests = []
    
    # فحص اتصال الإنترنت
    print("📡 فحص اتصال الإنترنت...")
    internet_ok = test_internet_connection()
    tests.append(internet_ok)
    print()
    
    # فحص yt-dlp
    print("📥 فحص yt-dlp...")
    yt_dlp_ok = test_yt_dlp()
    tests.append(yt_dlp_ok)
    print()
    
    # فحص ffmpeg
    print("🎬 فحص ffmpeg...")
    ffmpeg_ok = test_ffmpeg()
    tests.append(ffmpeg_ok)
    print()
    
    # فحص الوصول إلى يوتيوب
    if yt_dlp_ok and internet_ok:
        print("🌐 فحص الوصول إلى يوتيوب...")
        youtube_ok = test_youtube_access()
        tests.append(youtube_ok)
        print()
        
        # فحص البحث
        print("🔍 فحص البحث في يوتيوب...")
        search_ok = test_youtube_search()
        tests.append(search_ok)
        print()
        
        # فحص الترجمات
        print("📝 فحص دعم الترجمات...")
        subtitle_ok = test_subtitle_support()
        tests.append(subtitle_ok)
        print()
    else:
        print("⏭️ تخطي فحوصات يوتيوب (yt-dlp غير متوفر أو لا يوجد إنترنت)")
        print()
    
    # النتائج النهائية
    print("📊 النتائج النهائية:")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    
    if passed == total:
        print("🎉 جميع الفحوصات نجحت! التطبيق جاهز للاستخدام بالكامل.")
        print("✨ يمكنك الاستفادة من جميع الميزات المتقدمة.")
    elif passed >= total * 0.8:
        print("✅ معظم الفحوصات نجحت! التطبيق يعمل بشكل جيد.")
        print("⚠️ بعض الميزات المتقدمة قد لا تعمل بشكل مثالي.")
    elif passed >= total * 0.5:
        print("⚠️ بعض الفحوصات فشلت. التطبيق قد يعمل بشكل محدود.")
        print("🔧 يُنصح بإصلاح المشاكل المذكورة أعلاه.")
    else:
        print("❌ معظم الفحوصات فشلت. التطبيق لا يعمل بشكل صحيح.")
        print("🛠️ يُنصح بتثبيت المتطلبات الأساسية أولاً.")
    
    print(f"\n📈 النتيجة: {passed}/{total} فحص نجح")
    print("=" * 60)
    
    # نصائح إضافية
    if not ffmpeg_ok:
        print("\n💡 نصائح:")
        print("- لتثبيت ffmpeg على Windows: تحميل من https://ffmpeg.org/download.html")
        print("- لتثبيت ffmpeg على Linux: sudo apt install ffmpeg")
        print("- لتثبيت ffmpeg على macOS: brew install ffmpeg")

if __name__ == "__main__":
    main()
