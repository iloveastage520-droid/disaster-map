import os
import json
from datetime import datetime

# 設定路徑
metadata_dir = "metadata"
map_dir = "news_maps"
output_file = "index.html"

# 準備 HTML 開頭
html_head = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>新北市災情新聞地圖</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }
        h1 { color: #333; }
        .news-card { background: #fff; border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
        .news-card img { max-height: 150px; max-width: 200px; float: right; margin-left: 15px; }
        .summary { margin: 5px 0; }
        .timestamp { font-size: 0.9em; color: #666; }
        .btn-map { display: inline-block; margin-top: 8px; padding: 6px 10px; background: #007bff; color: #fff; text-decoration: none; border-radius: 4px; }
        .btn-map:hover { background: #0056b3; }
    </style>
</head>
<body>
<h1>🗺️ 新北市災情新聞地圖</h1>
"""

# 最後更新時間
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
html_head += f"<p>🕒 最後更新時間：{now}</p>\n"

# 準備新聞列表內容
news_cards = []

for filename in sorted(os.listdir(metadata_dir), reverse=True):
    if filename.endswith(".json"):
        json_path = os.path.join(metadata_dir, filename)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        map_file_path = os.path.join(map_dir, data.get("map_file", ""))
        if not os.path.exists(map_file_path):
            continue  # 沒有對應地圖就跳過

        news_card = f"""
        <div class="news-card">
            <img src="{data.get("image", "")}" alt="新聞縮圖">
            <h3><a href="{data.get("url", "#")}" target="_blank">{data.get("title", "")}</a></h3>
            <div class="summary">📰 {data.get("summary", "")}</div>
            <div class="timestamp">📅 爬搜時間：{data.get("timestamp", "")}</div>
            <a class="btn-map" href="{map_dir}/{data.get("map_file")}" target="_blank">🌐 查看地圖</a>
        </div>
        """
        news_cards.append(news_card)

# 組合全部 HTML
html_content = html_head + "\n".join(news_cards) + "\n</body>\n</html>"

# 寫入 index.html
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ 已更新 {output_file}")
