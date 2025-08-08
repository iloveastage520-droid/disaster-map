import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from news_to_cctv_single_input import analyze_news, match_cctv_for_keywords, generate_map_with_sidebar

# 新北市29區名稱關鍵字
newtaipei_districts = [
    "板橋", "三重", "中和", "永和", "新莊", "新店", "樹林", "鶯歌", "三峽", "淡水", "汐止", "瑞芳",
    "土城", "蘆洲", "五股", "泰山", "林口", "深坑", "石碇", "坪林", "三芝", "石門", "八里", "平溪",
    "雙溪", "貢寮", "金山", "萬里"
]

# 自動爬 ETtoday 社會新聞頁面
def crawl_ettoday_social_links():
    base_url = "https://www.ettoday.net/news/focus/%E7%A4%BE%E6%9C%83/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    r = requests.get(base_url, headers=headers, verify=False)  # 加入 verify=False 解決 SSL 問題
    soup = BeautifulSoup(r.text, "html.parser")
    links = []

    for a in soup.select(".part_list_2 a"):
        href = a.get("href", "")
        if href.startswith("/news/"):
            full_url = "https://www.ettoday.net" + href
            links.append(full_url)

    return links

# 主程式入口
if __name__ == "__main__":
    print("請選擇模式：")
    print("1️⃣ 輸入單一新聞網址")
    print("2️⃣ 自動爬 ETtoday 新北相關新聞")
    mode = input("請輸入 1 或 2：").strip()

    if mode == "1":
        news_url = input("請輸入 ETtoday 新聞網址：").strip()
        try:
            keywords, title, url, news_img = analyze_news(news_url)
            if any(d in keywords for d in newtaipei_districts):
                cctv_list = match_cctv_for_keywords(keywords)
                generate_map_with_sidebar(keywords, cctv_list, title, url, news_img)
            else:
                print("❌ 該新聞與新北市無關，未產出地圖")
        except Exception as e:
            print(f"⚠️ 解析錯誤：{e}")

    elif mode == "2":
        print("🔍 開始爬 ETtoday 社會新聞...")
        news_links = crawl_ettoday_social_links()
        print(f"共擷取到 {len(news_links)} 則新聞")

        count = 0
        for link in news_links:
            try:
                keywords, title, url, news_img = analyze_news(link)
                if any(d in keywords for d in newtaipei_districts):
                    print(f"✅ 處理新聞：{title}")
                    cctv_list = match_cctv_for_keywords(keywords)
                    generate_map_with_sidebar(keywords, cctv_list, title, url, news_img)
                    count += 1
            except Exception as e:
                print(f"⚠️ 解析錯誤：{e}")

        print(f"🎉 共成功處理 {count} 則與新北市有關的新聞")

    else:
        print("❌ 錯誤的選項，請輸入 1 或 2")
