import os
import re
import json
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import folium

# 📍 CCTV 資料讀入
CCTV_CSV = "newtaipeicity_cctv.csv"
with open(CCTV_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    CCTV_LIST = list(reader)

# 📍 新北市29區名稱
newtaipei_districts = [
    "板橋", "三重", "中和", "永和", "新莊", "新店", "樹林", "鶯歌", "三峽", "淡水", "汐止", "瑞芳",
    "土城", "蘆洲", "五股", "泰山", "林口", "深坑", "石碇", "坪林", "三芝", "石門", "八里", "平溪",
    "雙溪", "貢寮", "金山", "萬里"
]

# ✅ 爬 ETtoday 社會新聞連結
def crawl_ettoday_social_links():
    base_url = "https://www.ettoday.net/news/focus/%E7%A4%BE%E6%9C%83/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(base_url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.select(".part_list_2 a"):
        href = a.get("href", "")
        if href.startswith("/news/"):
            full_url = "https://www.ettoday.net" + href
            links.append(full_url)
    return list(set(links))  # 去除重複

# ✅ 分析新聞內容
def analyze_news(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)
    content_tags = soup.select(".story p")
    content = "\n".join(p.get_text(strip=True) for p in content_tags)
    summary = content[:60] + "..." if len(content) > 60 else content

    img_tag = soup.find("meta", property="og:image")
    news_img = img_tag["content"] if img_tag else ""

    # 提取關鍵地點字詞
    keywords = [district for district in newtaipei_districts if district in content]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    return keywords, title, url, news_img, summary, timestamp

# ✅ 比對 CCTV
def match_cctv_for_keywords(keywords):
    matched = []
    for row in CCTV_LIST:
        if any(keyword in row["location"] for keyword in keywords):
            matched.append(row)
    return matched

# ✅ 產製地圖與 metadata
def generate_map_with_sidebar(keywords, cctv_list, title, url, news_img, summary, timestamp):
    if not cctv_list:
        print("❌ 無對應 CCTV，略過地圖生成")
        return

    # 建立資料夾
    os.makedirs("news_maps", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)

    # 檔名格式
    safe_title = re.sub(r"[\\/:*?\"<>|]", "_", title)
    filename = f"cctv_map_sidebar_{datetime.now().strftime('%Y%m%d_%H%M')}"
    map_path = f"news_maps/{filename}.html"
    metadata_path = f"metadata/{filename}.json"

    # 建立地圖
    lat = float(cctv_list[0]["lat"])
    lon = float(cctv_list[0]["lon"])
    m = folium.Map(location=[lat, lon], zoom_start=13)

    for cam in cctv_list:
        folium.Marker(
            location=[float(cam["lat"]), float(cam["lon"])],
            popup=cam["location"],
            tooltip=cam["location"]
        ).add_to(m)

    m.save(map_path)

    # 寫入 metadata
    metadata = {
        "title": title,
        "summary": summary,
        "url": url,
        "news_img": news_img,
        "timestamp": timestamp,
        "keywords": keywords,
        "map_file": map_path
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ 地圖已產出：{map_path}")
