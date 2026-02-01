import requests
import re
import csv

# قائمة المصادر التي سيبحث فيها البوت
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
]

def check_link(url):
    """فحص سريع للتأكد من أن القناة تعمل"""
    try:
        r = requests.get(url, timeout=5, stream=True)
        return r.status_code == 200
    except:
        return False

def run_bot():
    valid_channels = []
    print("جاري جلب القنوات والبحث عن روابط شغالة...")
    
    for source in SOURCES:
        try:
            response = requests.get(source)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)', response.text)
            
            for name, url in matches:
                # نكتفي بجلب أول 20 قناة شغالة لضمان سرعة البوت
                if len(valid_channels) < 20:
                    clean_url = url.strip()
                    if check_link(clean_url):
                        valid_channels.append({
                            'id': len(valid_channels) + 1,
                            'title': name.strip(),
                            'image': 'https://via.placeholder.com/150?text=TV',
                            'url': clean_url
                        })
                        print(f"✅ تم العثور على قناة: {name.strip()}")
        except:
            continue

    # إعادة إنشاء ملف database.csv تلقائياً حتى لو كان محذوفاً
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'image', 'url'])
        writer.writeheader()
        writer.writerows(valid_channels)
    print("✅ تم إنشاء وتحديث ملف database.csv بنجاح!")

if __name__ == "__main__":
    run_bot()
