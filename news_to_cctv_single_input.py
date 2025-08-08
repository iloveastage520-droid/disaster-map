import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import folium
import urllib3
from datetime import datetime
import webbrowser
import json

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 讀取 CCTV 資料
cctv_df = pd.read_csv("newtaipeicity_cctv.csv", encoding="utf-8")

# 新北市29區名稱
alert_keywords = [
    "板橋", "三重", "中和", "永和", "新莊", "新店", "樹林", "鶯歌", "三峽", "淡水",
    "汐止", "瑞芳", "土城", "蘆洲", "五股", "泰山", "林口", "深坑", "石碇", "坪林",
    "三芝", "石門", "八里", "平溪", "雙溪", "貢寮", "金山", "萬里", "烏來"
]

# 地圖邊界模擬（未來可改用 GeoJSON）
district_polygons = {
    kw: [[[121.4, 25.0], [121.45, 25.0], [121.45, 25.05], [121.4, 25.05], [121.4, 25.0]]] for kw in alert_keywords
}

def extract_areas_fuzzy(text):
    return [kw for kw in alert_keywords if kw in text]

def is_stream_working(url):
    try:
        resp = requests.head(url, timeout=5, verify=False)
        return resp.status_code == 200
    except:
        return False

def match_cctv_for_keywords(keywords):
    results = []
    for kw in keywords:
        subset = cctv_df[cctv_df['district'].str.contains(kw)]
        for _, row in subset.iterrows():
            live_url = f"https://cctvatis4.ntpc.gov.tw/{row['areacode']}"
            if is_stream_working(live_url):
                results.append({
                    "keyword": kw,
                    "areacode": row['areacode'],
                    "district": row['district'],
                    "address": row.get('address', ''),
                    "latitude": row['latitude'],
                    "longitude": row['longitude'],
                    "live_url": live_url
                })
    return results

def analyze_news(news_url):
    r = requests.get(news_url, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    # 新聞標題
    title_tag = soup.select_one("h1.title") or soup.select_one("h1.article-title") or soup.title
    title = title_tag.get_text(strip=True) if title_tag else "新聞標題"

    # 新聞摘要（取前段文字）
    paragraphs = soup.find_all("p")
    summary = ""
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 20:
            summary = text[:100] + "..."
            break

    # 新聞圖示（若無就用預設）
    img_tag = soup.select_one(".story .cover img") or soup.find("img")
    news_img = img_tag.get("src") if img_tag else "https://cdn2.ettoday.net/images/8309/d8309921.jpg"

    # 新聞內文地點擷取
    fulltext = soup.get_text()
    keywords = extract_areas_fuzzy(fulltext)

    print("📍 偵測到地點：", keywords)
    return keywords, title, news_url, news_img, summary

def generate_map_with_sidebar(keywords, cctv_list, title, news_url, news_img, summary):
    if cctv_list:
        center_lat = cctv_list[0]['latitude']
        center_lon = cctv_list[0]['longitude']
    else:
        center_lat, center_lon = 25.0169, 121.4628

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    for kw in keywords:
        if kw in district_polygons:
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in district_polygons[kw][0]],
                color="red", fill=True, fill_opacity=0.3,
                tooltip=f"示警區域：{kw}"
            ).add_to(m)

    for c in cctv_list:
        folium.Marker(
            location=[c['latitude'], c['longitude']],
            tooltip=f"{c['district']} ({c['keyword']})",
            icon=folium.Icon(color="blue", icon="camera", prefix="fa")
        ).add_to(m)

    # 側邊欄 HTML
    sidebar_html = f"""
    <div id='sidebar' style='position:fixed; top:0; left:0; width:380px; height:100%; 
        overflow-y:auto; background:white; padding:10px; z-index:9999; border-right:2px solid black;'>
        <h3>{title}</h3>
        <a href='{news_url}' target='_blank'>前往新聞連結</a>
        <p>{summary}</p>
        <img src='{news_img}' width='350' style='margin-bottom:10px;'>
        <hr>
        <div style='display:flex; flex-wrap:wrap; gap:8px;'>
    """
    for c in cctv_list:
        sidebar_html += f"""
        <div style='flex:1 1 48%; padding:5px; border:1px solid #ccc;'>
            <b>{c['district']}</b><br>
            <small>{c['address']}</small><br>
            <img src='{c['live_url']}' width='160' height='120'>
        </div>
        """
    sidebar_html += "</div></div>"
    m.get_root().html.add_child(folium.Element(sidebar_html))

    # 調整地圖樣式
    m.get_root().html.add_child(folium.Element("""
    <style>
    #map { position: absolute; top: 0; left: 380px; right: 0; bottom: 0; }
    </style>
    """))

    # 儲存地圖與 metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = f"cctv_map_sidebar_{timestamp}"
    base_path = os.path.dirname(os.path.abspath(__file__))
    map_folder = os.path.join(base_path, "news_maps")
    meta_folder = os.path.join(base_path, "metadata")
    os.makedirs(map_folder, exist_ok=True)
    os.makedirs(meta_folder, exist_ok=True)

    html_path = os.path.join(map_folder, f"{file_id}.html")
    json_path = os.path.join(meta_folder, f"{file_id}.json")

    m.save(html_path)
    metadata = {
        "title": title,
        "url": news_url,
        "summary": summary,
        "thumbnail": news_img,
        "timestamp": timestamp,
        "cctv_count": len(cctv_list),
        "matched_keywords": keywords,
        "output_file": html_path
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ 已產出地圖：{html_path}")
    webbrowser.open(f"file://{html_path}")
