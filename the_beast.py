import feedparser
import csv
import os
import requests
import re
from typing import Dict

# المصادر التي حددتها
SOURCES = [
    "https://nyaa.si/?page=rss",
    "https://www.tokyotosho.info/rss.php"
]
DB_FILE = 'database.csv'

def translate_to_arabic(text):
    """ترجمة عناوين الأنمي إلى العربية باستخدام محرك ترجمة سريع"""
    try:
        # استخدام API بسيط للترجمة (Google Translate Free API)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5)
        return res.json()[0][0][0]
    except:
        return text # في حال فشل الترجمة يرجع النص الأصلي

def check_torrent_health(url):
    """5 & 6: فحص الرابط إذا كان يعمل"""
    if url.startswith('magnet:'): return True
    try:
        r = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        return r.status_code < 400
    except:
        return False

def start_bot():
    # 4: الحفاظ على البيانات القديمة (تراكمي)
    database = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    database[row['name_en']] = row
        except: pass

    headers = {'User-Agent': 'Mozilla/5.0'}
    print("📡 جاري قنص وترجمة روابط التورنت...")

    for rss_url in SOURCES:
        try:
            resp = requests.get(rss_url, headers=headers, timeout=15)
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:20]: # 3: سحب الجديد
                name_en = entry.title
                torrent_url = entry.link
                
                # منع التكرار وفحص الرابط
                if name_en not in database or not check_torrent_health(database[name_en]['torrent_url']):
                    print(f"🆕 معالجة: {name_en}")
                    
                    # ترجمة العنوان للعربية
                    name_ar = translate_to_arabic(name_en)
                    
                    # 1 & 2: جدول بالاسم العربي، الإنجليزي، والرابط
                    database[name_en] = {
                        'name_ar': name_ar,
                        'name_en': name_en,
                        'torrent_url': torrent_url,
                        'status': 'يعمل ✅'
                    }
        except Exception as e:
            print(f"❌ خطأ في المصدر: {e}")

    # حفظ النتائج (القديم والجديد)
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name_ar', 'name_en', 'torrent_url', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(database.values())
    print(f"✨ تم التحديث! إجمالي العناصر المترجمة: {len(database)}")

if __name__ == "__main__":
    start_bot()
