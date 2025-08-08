from datetime import datetime
import os
import json

metadata_folder = "metadata"
output_file = "index.html"

def generate_index_html():
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>災情地圖總覽</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            h1 {{ color: #333; }}
            .card {{ background: white; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }}
            .card img {{ width: 160px; height: auto; float: right; margin-left: 20px; }}
            .card h2 {{ margin-top: 0; }}
            .card p {{ clear: both; }}
            .timestamp {{ font-size: 0.9em; color: #888; }}
        </style>
    </head>
    <body>
        <h1>📍 災情地圖總覽</h1>
        <p class='timestamp'>最後更新時間：{update_time}</p>
    """

    count = 0
    for file in sorted(os.listdir(metadata_folder), reverse=True):
        if file.endswith(".json"):
            with open(os.path.join(metadata_folder, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                html_filename = data.get("html_filename", "")
                if not os.path.exists(os.path.join("news_maps", html_filename)):
                    continue  # 略過沒有對應 HTML 的

                html += f"""
                <div class='card'>
                    <img src='{data.get('news_img', '')}' alt='news image'>
                    <h2>{data.get('title', '無標題')}</h2>
                    <p>{data.get('summary', '')}</p>
                    <p class='timestamp'>🕒 爬搜時間：{data.get('timestamp', '')}</p>
                    <p><a href='news_maps/{html_filename}' target='_blank'>👉 點我查看地圖頁面</a></p>
                </div>
                """
                count += 1

    html += """
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 已更新首頁 index.html（共載入 {count} 筆）")

if __name__ == "__main__":
    generate_index_html()
