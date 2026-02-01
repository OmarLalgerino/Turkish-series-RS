import feedparser
import csv
import requests
import re
import cloudscraper
import os

SOURCES = [
    "https://nyaa.si/?page=rss&q=Arabic+1080p",
    "https://nyaa.si/?page=rss&q=Arabic+720p",
    "https://nyaa.si/?page=rss&q=Arabic+480p",
    "https://www.tokyotosho.info/rss.php?filter=1,11&z=Arabic"
]

MAX_ROWS = 10000 

def get_current_db_file():
    i = 0
    while True:
        filename = f'database_{i}.csv' if i > 0 else 'database.csv'
        if not os.path.exists(filename):
            return filename
        with open(filename, 'r', encoding='utf-8') as f:
            row_count = sum(1 for row in f)
        if row_count < MAX_ROWS:
            return filename
        i += 1

def translate_to_arabic_only(text):
    # تنظيف العنوان من كل الرموز والكلمات الإنجليزية قبل حفظه
    clean_text = re.sub(r'\[.*?\]|\(.*?\)|1080p|720p|480p|HEVC|x264|x265|AAC|Vostfr', '', text).strip()
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ar&dt=t&q={requests.utils.quote(clean_text)}"
        res = requests.get(url, timeout=5)
        return res.json()[0][0][0] # إرجاع النص العربي فقط
    except:
        return "عنوان غير معروف"

def get_clean_hash_link(entry):
    if hasattr(entry, 'nyaa_infohash'):
        return f"https://webtor.io/player/embed/{entry.nyaa_infohash}"
    link = getattr(entry, 'link', '')
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', link)
    if hash_match:
        return f"https://webtor.io/player/embed/{hash_match.group(1).lower()}"
    return None

def start_bot():
    scraper = cloudscraper.create_scraper()
    db_file = get_current_db_file()
    print(f"🚀 جاري الحفظ في الملف العربي: {db_file}")

    entries_to_save = []
    for rss_url in SOURCES:
        try:
            resp = scraper.get(rss_url, timeout=15)
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:30]:
                link = get_clean_hash_link(entry)
                if link:
                    # تحويل الاسم للعربي فوراً
                    arabic_title = translate_to_arabic_only(entry.title)
                    
                    # تحديد الجودة بالعربي
                    if "1080p" in entry.title: q = "1080p عالية"
                    elif "720p" in entry.title: q = "720p متوسطة"
                    else: q = "480p سريعة"
                    
                    # لاحظ هنا: لا يوجد name_en أبداً
                    entries_to_save.append({
                        'اسم_الأنمي': arabic_title,
                        'الرابط': link,
                        'الجودة': q
                    })
        except:
            continue

    file_exists = os.path.isfile(db_file)
    with open(db_file, 'a', newline='', encoding='utf-8') as f:
        # رؤوس الأعمدة بالعربية فقط
        columns = ['اسم_الأنمي', 'الرابط', 'الجودة']
        writer = csv.DictWriter(f, fieldnames=columns)
        if not file_exists or os.stat(db_file).st_size == 0:
            writer.writeheader()
        writer.writerows(entries_to_save)
    
    print(f"✅ تم! الملف الآن عربي خالص وبدون أي خانات إنجليزية.")

if __name__ == "__main__":
    start_bot()
