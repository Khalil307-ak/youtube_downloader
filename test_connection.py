#!/usr/bin/env python3
"""
ملف تشخيص بسيط لفحص التطبيق
"""

import subprocess
import sys
import json

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

def main():
    print("🔍 فحص التطبيق...")
    print("=" * 50)
    
    # فحص yt-dlp
    yt_dlp_ok = test_yt_dlp()
    print()
    
    # فحص الوصول إلى يوتيوب
    if yt_dlp_ok:
        youtube_ok = test_youtube_access()
        print()
        
        if youtube_ok:
            print("🎉 جميع الفحوصات نجحت! التطبيق جاهز للاستخدام.")
        else:
            print("⚠️ هناك مشكلة في الوصول إلى يوتيوب. تحقق من اتصال الإنترنت.")
    else:
        print("❌ يجب تثبيت yt-dlp أولاً.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
