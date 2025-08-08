import os
import json
from datetime import datetime
import folium
from folium.plugins import MarkerCluster

def generate_map_with_sidebar(keywords, cctv_list, title, url, news_img):
    # ✅ 檔名處理
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
    html_filename = f"cctv_map_sidebar_{timestamp}.html"

    # ✅ 地圖初始化
    if cctv_list:
        avg_lat = sum(float(c['lat']) for c in cctv_list) / len(cctv_list)
        avg_lon = sum(float(c['lon']) for c in cctv_list) / len(cctv_list)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    else:
        m = folium.Map(location=[25.016982, 121.462786], zoom_start=11)  # 新北市中心預設值

    # ✅ 標註 CCTV 點位
    marker_cluster = MarkerCluster().add_to(m)
    for c in cctv_list:
        folium.Marker(
            location=[float(c['lat']), float(c['lon'])],
            popup=f"<b>{c['name']}</b><br><a href='{c['url']}' target='_blank'>觀看即時影像</a>",
            icon=folium.Icon(color='blue', icon='camera')
        ).add_to(marker_cluster)

    # ✅ 輸出到資料夾
    map_dir = "news_maps"
    os.makedirs(map_dir, exist_ok=True)
    map_path = os.path.join(map_dir, html_filename)
    m.save(map_path)

    # ✅ 同步寫入 metadata JSON
    metadata = {
        "title": title,
        "summary": "、".join(keywords[:8]),  # 可再優化為 NLP 摘要
        "url": url,
        "image": news_img,
        "map_file": html_filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    meta_dir = "metadata"
    os.makedirs(meta_dir, exist_ok=True)
    json_path = os.path.join(meta_dir, f"{html_filename.replace('.html', '.json')}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ 已產出地圖：{map_path}")
    print(f"📝 已儲存摘要：{json_path}")
