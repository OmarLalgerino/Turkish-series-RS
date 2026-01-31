import cloudscraper
from bs4 import BeautifulSoup
import csv
import os

scraper = cloudscraper.create_scraper()

def get_video_links(page_url):
    links = {"1080p": "", "720p": "", "480p": ""}
    try:
        # الدخول لصفحة الحلقة
        res = scraper.get(page_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # البحث عن المشغل المباشر (Iframe)
        # أغلب المواقع تضع الرابط في وسم iframe
        iframe = soup.find('iframe', src=True)
        if iframe:
            video_url = iframe['src']
            if video_url.startswith('//'): video_url = 'https:' + video_url
            # نضع الرابط في جودة 720p كافتراضي
            links["720p"] = video_url
        
        # محاولة البحث عن روابط MP4 مباشرة في الكود
        import re
        found_links = re.findall(r'(https?://[^\s\'"]+\.(?:mp4|m3u8))', res.text)
        if found_links:
            links["1080p"] = found_links[0]

        return links
    except:
        return links

def update_database():
    # الرابط الذي أثبت نجاحه في صورتك
    source_url = "https://mycima.gold/category/series/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/"
    db_file = 'database.csv'
    all_data = []

    try:
        res = scraper.get(source_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.find_all('div', class_='GridItem')

        for item in items[:10]: # فحص أول 10 حلقات
            name = item.find('strong').text.strip() if item.find('strong') else "حلقة"
            link = item.find('a')['href']
            
            print(f"📡 جاري استخراج رابط: {name}")
            v_links = get_video_links(link)
            
            all_data.append({
                'name': name,
                'url_1080p': v_links['1080p'],
                'url_720p': v_links['720p'],
                'url_480p': v_links['480p']
            })

        # حفظ البيانات
        with open(db_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url_1080p', 'url_720p', 'url_480p'])
            writer.writeheader()
            writer.writerows(all_data)
        print("✅ تم تحديث الروابط!")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    update_database()
