import requests
from bs4 import BeautifulSoup
import json

# رابط الـ Web App الخاص بجدول جوجل (الذي حصلت عليه من Apps Script)
SHEET_API_URL = "ضع_رابط_الـ_WEB_APP_هنا"

def scrape_3sk(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. جلب اسم المسلسل والحلقة
        title = soup.find('h1').text.strip() if soup.find('h1') else "مسلسل تركي"

        # 2. جلب روابط الجودات (SD, HD, FHD)
        # الموقع يضع الروابط في أزرار أو داخل المشغل
        links = {"FHD": "", "HD": "", "SD": ""}
        
        # البحث عن أزرار المشاهدة
        sources = soup.find_all('source') or soup.find_all('a', href=True)
        
        for item in sources:
            href = item.get('href') or item.get('src')
            if href:
                if "1080" in href or "fhd" in href.lower(): links["FHD"] = href
                elif "720" in href or "hd" in href.lower(): links["HD"] = href
                elif "480" in href or "sd" in href.lower(): links["SD"] = href

        # إذا لم يجد روابط مباشرة، سيأخذ رابط المشاهدة الأساسي
        if not links["HD"]:
            iframe = soup.find('iframe')
            if iframe: links["HD"] = iframe['src']

        # 3. إرسال البيانات إلى Google Sheets
        payload = {
            "name": title,
            "fhd": links["FHD"],
            "hd": links["HD"],
            "sd": links["SD"]
        }
        
        requests.post(SHEET_API_URL, json=payload)
        print(f"✅ تم بنجاح: {title}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

# تشغيل السكربت على الرابط الذي أعطيتني إياه
scrape_3sk("https://k.3sk.media/o5p4/")
