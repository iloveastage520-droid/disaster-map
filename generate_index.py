import os
import json
from datetime import datetime

# 資料夾設定
base_folder = os.path.dirname(os.path.abspath(__file__))
metadata_folder = os.path.join(base_folder, "metadata")
news_map_folder = "news_maps"
index_file_path = os.path.join(base_folder, "index.html")

# 掃描 metadata 資料夾
entries = []
for filename in os.listdir(metadata_folder):
    if filename.endswith(".json"):
        with open(os.path.join(metadata_folder, filename), "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                entries.append(data)
            except Exception as e:
                print(f"⚠️ 無法讀取 {filename}：{e}")

# 依時間排序（新到舊）
entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

# 產出 HTML 內容
html = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>災情即時地圖總覽</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 0; background: #f0f0f0; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        .entry { background: #fff; border-radius: 6px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; gap: 15px; }
        .entry img { width: 160px; height: auto; border-radius: 4px; object-fit: cover; }
        .entry .info { flex: 1; }
        .entry h2 { margin: 0 0 10px; font-size: 18px; }
        .entry p { margin: 0 0 5px; color: #555; }
        .entry a.map-link { display: inline-block; margin-top: 8px; color: #007BFF; text-decoration: none; }
        .entry a.map-link:hover { text-decoration: underline; }
        h1 { text-align: center; margin-bottom: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 災情新聞地圖總覽</h1>
"""

for entry in entries:
    title = entry.get("title", "未命名新聞")
    summary = entry.get("summary", "（無摘要）")
    img_url = entry.get("img_url", "")
    map_path = entry.get("map_path", "#")
    timestamp = entry.get("timestamp", "")[:16].replace("T", " ")  # 簡化時間

    html += f"""
        <div class="entry">
            <img src="{img_url}" alt="news">
            <div class="info">
                <h2>{title}</h2>
                <p>{summary}</p>
                <p><small>🕒 {timestamp}</small></p>
                <a class="map-link" href="{map_path}" target="_blank">🌐 查看對應地圖</a>
            </div>
        </div>
    """

html += """
    </div>
</body>
</html>
"""

# 寫入 index.html
with open(index_file_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 已產出首頁 index.html，共顯示 {len(entries)} 筆災情地圖。")
