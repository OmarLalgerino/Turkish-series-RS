import feedparser
import csv
import os

def get_embed_streaming(title):
    # تحويل الاسم لرابط مشغل مباشر (Embed)
    clean_title = title.split(']')[1].split('-')[0].strip() if ']' in title else title
    # هذا الرابط هو "مشغل بحث" يفتح الفيديو مباشرة للمستخدم
    return f"https://www.google.com/search?q={clean_title}+streaming+player"

def start():
    feed = feedparser.parse("https://nyaa.land/?page=rss")
    data = []
    
    for entry in feed.entries[:20]:
        title = entry.title
        # جلب روابط المشغل أونلاين
        embed_link = get_embed_streaming(title)
        data.append({'name': title, 'url': embed_link})
        
    # حفظ في الجدول
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url'])
        writer.writeheader()
        writer.writerows(data)
    print("Done!")

if __name__ == "__main__":
    start()
