import requests
import re
import csv

def test_link(url):
    """يختبر إذا كان الرابط يعمل ويعيد True أو False"""
    try:
        # نرسل طلب "HEAD" بدلاً من "GET" ليكون الفحص سريعاً جداً ولا يستهلك بيانات
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def fetch_and_filter():
    # مصدر القنوات (مثال: قنوات عربية)
    source_url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
    
    print("جاري جلب قائمة القنوات...")
    response = requests.get(source_url)
    if response.status_code != 200:
        return []

    # استخراج الاسم والرابط
    pattern = r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)'
    matches = re.findall(pattern, response.text)
    
    valid_channels = []
    count = 0
    max_channels = 50  # حددنا 50 قناة فقط لأن الفحص يأخذ وقتاً

    print(f"تم العثور على {len(matches)} قناة. يبدأ الفحص الآن...")

    for name, url in matches:
        if count >= max_channels:
            break
        
        clean_url = url.strip()
        # اختبار الرابط قبل إضافته
        if test_link(clean_url):
            print(f"✅ تعمل: {name.strip()}")
            valid_channels.append({
                'id': count + 1,
                'title': name.strip(),
                'image': 'https://via.placeholder.com/150?text=TV',
                'url': clean_url
            })
            count += 1
        else:
            print(f"❌ معطلة: {name.strip()}")

    return valid_channels

def save_to_csv(channels):
    if not channels:
        print("لا توجد قنوات صالحة للإضافة.")
        return
    
    keys = ['id', 'title', 'image', 'url']
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(channels)
    print(f"✅ تم تحديث الجدول بـ {len(channels)} قناة شغالّة!")

# تشغيل البوت
if __name__ == "__main__":
    live_data = fetch_and_filter()
    save_to_csv(live_data)
