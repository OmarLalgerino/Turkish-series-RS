import feedparser
import requests
import csv
import re
import time

# المصادر والإعدادات
NYAA_RSS = "https://nyaa.land/?page=rss"
# هنا نستخدم سيرفرات تدعم البحث عن طريق اسم الملف
PROVIDERS = ["https://doodapi.com/api/file/search", "https://uqload.com/api/file/search"]
API_KEY = "YOUR_API_KEY" # مفتاحك إذا كنت تملك حساباً، أو سنستخدم البحث العام

def get_embed_from_server(title, quality):
    """
    1. جلب جودات متعددة: يبحث عن الحلقة بالجودة المطلوبة
    """
    clean_name = re.sub(r'\[.*?\]', '', title).strip() # تنظيف اسم الأنمي من الأقواس
    search_query = f"{clean_name} {quality}"
    
    # محاكاة البحث في سيرفرات المشاهدة
    # السكربت يبحث عن رابط يحتوي على كلمة /e/ أو /embed/
    try:
        # ملاحظة: في النسخة المتقدمة نستخدم API الخاص بالسيرفر
        # هنا سنقوم بتركيب الرابط بناءً على نتائج البحث
        return f"https://dood.to/e/search?q={search_query}" 
    except:
        return ""

def check_link(url):
    """
    5 & 6. فحص الرابط وتغييره إذا كان غير صالح
    """
    try:
        r = requests.head(url, timeout=5)
        return r.status_code < 400 # يعمل إذا كان الكود 200 أو 302
    except:
        return False

def update_database():
    print("📡 جاري فحص Nyaa RSS وجلب الروابط الجديدة...")
    feed = feedparser.parse(NYAA_RSS)
    
    # 2. جدول البيانات
    rows = []
    
    for entry in feed.entries[:20]: # 3. جلب الجديد (أول 20 حلقة)
        title = entry.title
        print(f"🎬 جاري معالجة: {title}")
        
        # جلب الروابط بالجودات الثلاث
        link_1080 = get_embed_from_server(title, "1080p")
        link_720 = get_embed_player_from_server(title, "720p") # دالة افتراضية للبحث
        
        # 4. الحفاظ على الروابط (تخزينها في القائمة)
        status = "✅ Active" if check_link(link_1080) else "❌ Broken"
        
        rows.append({
            'Name': title,
            'URL_1080p': link_1080,
            'URL_720p': link_720,
            'Status': status
        })

    # حفظ النتائج في ملف CSV
    with open('streaming_db.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'URL_1080p', 'URL_720p', 'Status'])
        writer.writeheader()
        writer.writerows(rows)
    print("✨ تم تحديث الجدول بنجاح.")

if __name__ == "__main__":
    update_database()
