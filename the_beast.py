import cloudscraper
from bs4 import BeautifulSoup
import csv
import os

def scrape_to_csv(url):
    # استخدام scraper لتجاوز الحماية
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. استخراج الاسم (تنظيفه ليكون احترافياً)
        title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Series"
        
        # 2. استخراج رابط المشاهدة (الجودة الأعلى المتوفرة)
        watch_link = ""
        # البحث عن سيرفرات المشاهدة
        iframe = soup.find('iframe')
        if iframe:
            watch_link = iframe.get('src', '')

        if not watch_link:
            # محاولة البحث في الأزرار إذا لم يوجد iframe
            for a in soup.find_all('a', href=True):
                if "watch" in a['href'] or "video" in a['href']:
                    watch_link = a['href']
                    break

        # 3. حفظ البيانات في ملف CSV بترتيب (اسم، رابط)
        file_exists = os.path.isfile('database.csv')
        
        with open('database.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # إذا كان الملف جديداً، أضف العناوين (Headers)
            if not file_exists:
                writer.writerow(['name', 'url'])
            
            # إضافة السطر الجديد
            writer.writerow([title, watch_link])
            
        print(f"✅ تم بنجاح إضافة: {title}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

# الرابط المستهدف
target_url = "https://k.3sk.media/o5p4/"
scrape_to_csv(target_url)
