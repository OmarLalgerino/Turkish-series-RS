import requests
import re
import csv

# مصادر جلب القنوات
SOURCES = ["https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"]

def check_link(url):
    """يختبر الرابط بسرعة للتأكد من أنه يعمل (Status 200)"""
    try:
        r = requests.get(url, timeout=5, stream=True)
        return r.status_code == 200
    except:
        return False

def start_bot():
    valid_data = []
    print("جاري البحث عن روابط m3u8 شغالة...")
    
    try:
        response = requests.get(SOURCES[0])
        # استخراج الاسم والرابط من ملفات m3u
        matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)', response.text)
        
        for name, url in matches:
            if len(valid_data) < 20: # نكتفي بـ 20 قناة لضمان سرعة الفحص
                clean_url = url.strip()
                if check_link(clean_url):
                    valid_data.append({
                        'id': len(valid_data) + 1,
                        'title': name.strip(),
                        'image': 'https://via.placeholder.com/150?text=TV',
                        'url': clean_url
                    })
                    print(f"✅ تم العثور على قناة: {name.strip()}")
    except Exception as e:
        print(f"حدث خطأ: {e}")

    # إعادة إنشاء ملف database.csv حتى لو كان محذوفاً
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'image', 'url'])
        writer.writeheader()
        writer.writerows(valid_data)
    print("✅ تم إنشاء وتحديث الجدول بنجاح!")

if __name__ == "__main__":
    start_bot()
