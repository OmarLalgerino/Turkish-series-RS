import cloudscraper
import re
import csv
from bs4 import BeautifulSoup

# إعداد القناص
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'android','desktop': False})

def get_links_from_server(page_url):
    """هذا هو الكود الذي سألت عنه، يقوم بسحب الروابط من سيرفرات الآخرين"""
    links = {"1080p": "", "720p": "", "480p": ""}
    try:
        res = scraper.get(page_url, timeout=15)
        html = res.text
        
        # البحث عن سيرفر Uqload
        uq_match = re.search(r'https?://(?:uqload\.com|uqload\.co)/embed-([a-z0-9]+)', html)
        if uq_match:
            links["1080p"] = f"https://uqload.com/embed-{uq_match.group(1)}.html"
            
        # البحث عن سيرفر DoodStream
        dood_match = re.search(r'https?://(?:doodstream\.com|dood\.to|dood\.so)/e/([a-z0-9]+)', html)
        if dood_match:
            links["720p"] = f"https://dood.to/e/{dood_match.group(1)}"
            
        # البحث عن سيرفر Upstream
        up_match = re.search(r'https?://(?:upstream\.to|upstream\.org)/embed-([a-z0-9]+)', html)
        if up_match:
            links["480p"] = f"https://upstream.to/embed-{up_match.group(1)}.html"
            
        return links
    except:
        return links

def start_hunting():
    # الموقع المستهدف (واجهة المسلسلات)
    target_site = "https://wecima.show/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/"
    db_file = 'database.csv'
    all_results = []

    print(f"🚀 جاري بدء عملية السحب من السيرفرات...")
    try:
        response = scraper.get(target_site)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن كروت الحلقات (تأكد أن الكلاس GridItem صحيح للموقع)
        items = soup.find_all('div', class_='GridItem')

        for item in items[:15]:
            title = item.find('strong').text.strip() if item.find('strong') else "حلقة غير معروفة"
            page_link = item.find('a')['href']
            
            print(f"🔍 فحص السيرفرات لـ: {title}")
            server_links = get_links_from_server(page_link)
            
            all_results.append({
                'name': title,
                'url_1080p': server_links['1080p'],
                'url_720p': server_links['720p'],
                'url_480p': server_links['480p']
            })

        # حفظ البيانات في الملف النهائي
        with open(db_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url_1080p', 'url_720p', 'url_480p'])
            writer.writeheader()
            writer.writerows(all_results)
        print("✨ انتهى! اذهب الآن لملف database.csv وستجد روابط السيرفرات جاهزة.")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    start_hunting()
