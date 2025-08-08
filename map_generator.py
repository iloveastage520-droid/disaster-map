import os
import json
import re
from datetime import datetime
import folium
from folium import Map, Marker, Icon, Polygon, Element

# 預設簡化的區域多邊形（可替換為完整新北市29區）
district_polygons = {
    "樹林": [[[121.39, 24.98], [121.42, 24.98], [121.42, 25.01], [121.39, 25.01], [121.39, 24.98]]],
    "三峽": [[[121.34, 24.91], [121.39, 24.91], [121.39, 24.95], [121.34, 24.95], [121.34, 24.91]]],
    "土城": [[[121.42, 24.96], [121.47, 24.96], [121.47, 25.00], [121.42, 25.00], [121.42, 24.96]]]
}

# 建立簡易摘要
def extract_summary_from_title(title):
    return title[:50] + "..." if len(title) > 50 else title

# 主函數
def generate_map_with_sidebar(keywords, cctv_list, title, news_url, news_img):
    if cctv_list:
        center_lat = cctv_list[0]['latitude']
        center_lon = cctv_list[0]['longitude']
    else:
        center_lat, center_lon = 25.0169, 121.4628

    m = Map(location=[center_lat, center_lon], zoom_start=12)

    # 多邊形警示區
    for kw in keywords:
        if kw in district_polygons:
            Polygon(
                locations=[(lat, lon) for lon, lat in district_polygons[kw][0]],
                color="red",
                fill=True,
                fill_opacity=0.3,
                tooltip=f"示警區域：{kw}"
            ).add_to(m)

    # CCTV 標記
    for c in cctv_list:
        Marker(
            location=[c['latitude'], c['longitude']],
            tooltip=f"{c['district']} ({c['keyword']})",
            icon=Icon(color="blue", icon="camera", prefix="fa")
        ).add_to(m)

    # 側邊欄
    sidebar_html = f"""
    <div id="sidebar" style="position:fixed; top:0; left:0; width:380px; height:100%;
        overflow-y:auto; background:white; padding:10px; z-index:9999; border-right: 2px solid black;">
        <h3>新聞示警區域</h3>
        <p><b>新聞：</b><a href="{news_url}" target="_blank">{title}</a></p>
        <img src="{news_img}" width="350" style="margin-bottom:15px;">
        <div style='display:flex; flex-wrap:wrap; gap:5px;'>"""

    for c in cctv_list:
        sidebar_html += f"""
        <div style="flex:1 1 48%; background:#f9f9f9; padding:5px; border:1px solid #ccc;">
            <b>{c['district']}</b> ({c['areacode']})<br>
            <small>{c['address']}</small><br>
            <img src="{c['live_url']}" width="160" height="120">
        </div>"""

    sidebar_html += "</div></div>"

    m.get_root().html.add_child(Element(sidebar_html))
    m.get_root().html.add_child(Element("""
        <style>
        #map { position: absolute; top: 0; left: 380px; right: 0; bottom: 0; }
        </style>
    """))

    # 儲存位置與檔名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title[:20])
    filename = f"{timestamp}_{safe_title}.html"

    output_folder = r"C:\Users\NCDR001\OneDrive\桌面\ArronProgram\Climp Media\news_maps"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename)
    m.save(output_path)
    print(f"✅ 地圖已產生：{output_path}")

    # 儲存 metadata
    metadata_folder = r"C:\Users\NCDR001\OneDrive\桌面\ArronProgram\Climp Media\metadata"
    os.makedirs(metadata_folder, exist_ok=True)
    metadata = {
        "title": title,
        "url": news_url,
        "image": news_img,
        "summary": extract_summary_from_title(title),
        "map_file": filename
    }
    metadata_path = os.path.join(metadata_folder, f"{timestamp}_{safe_title}.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"📝 Metadata 已儲存：{metadata_path}")
