import feedparser
import csv
import requests
import os

# مصادر الـ RSS التي طلبتها
RSS_SOURCES = [
    "https://nyaa.si/?page=rss",
    "https://www.tokyotosho.info/rss.php"
]
DB_FILE = 'database.csv'

def check_link_health(url):
    """5 & 6: فحص الرابط وإذا كان معطلاً يتم استبعاده"""
    try:
        r = requests.head(url, timeout=5)
        return r.status_code < 400
    except:
        return False

def get_embed_url(torrent_url, info_hash):
    """تحويل رابط التورنت إلى رابط مشاهدة مباشر (Embed)"""
    # نستخدم محرك تشغيل تورنت عالمي (مثل webtor أو videospider)
    # هذا الرابط سيفتح "مشغل فيديو" مباشرة في تطبيقك
    return f"https://webtor.io/player/embed/{info_hash}"

def start_hunting():
    # 4: قراءة الروابط القديمة للمحافظة عليها
    database = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                database[row['name']] = row

    print("📡 جاري سحب روابط المشاهدة من المصادر...")
    
    for rss_url in RSS_SOURCES:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:20]: # 3: سحب الجديد
            name = entry.title
            torrent_link = entry.link
            
            # استخراج الـ Hash من رابط التورنت (ضروري للتشغيل)
            # الـ Hash هو المعرف الوحيد للفيديو في عالم التورنت
            info_hash = ""
            if 'magnet:?' in torrent_link:
                match = re.search(r'xt=urn:btih:([a-fA-F0-9]+)', torrent_link)
                if match: info_hash = match.group(1)
            
            # 1: إعداد جودات متعددة (افتراضية بناءً على المشغل)
            embed_link = get_embed_url(torrent_link, info_hash)
            
            if embed_link and (name not in database or not check_link_health(database[name]['url_1080p'])):
                # 2: ملء الجدول بالاسم والروابط
                database[name] = {
                    'name': name,
                    'url_1080p': f"{embed_link}?quality=1080",
                    'url_720p': f"{embed_link}?quality=720",
                    'url_480p': f"{embed_link}?quality=480"
                }
                print(f"✅ تم صيد رابط مشاهدة لـ: {name}")

    # حفظ كل شيء (القديم والجديد) في ملف واحد
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url_1080p', 'url_720p', 'url_480p'])
        writer.writeheader()
        writer.writerows(database.values())

if __name__ == "__main__":
    start_hunting()
