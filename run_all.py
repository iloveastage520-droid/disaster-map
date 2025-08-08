import os
import subprocess
from datetime import datetime
from news_to_cctv_single_input import (
    crawl_ettoday_social_links,
    analyze_news,
    match_cctv_for_keywords,
    generate_map_with_sidebar,
    newtaipei_districts,
)
from generate_index import generate_index_html

# ---------- 路徑設定 ----------
output_folder = "news_maps"

# ---------- 主程式 ----------
def run_all():
    print("🚀 開始爬 ETtoday 新北市新聞...")
    news_links = crawl_ettoday_social_links()
    print(f"共擷取到 {len(news_links)} 則新聞")

    count = 0
    for url in news_links:
        try:
            keywords, title, url, news_img, summary, timestamp = analyze_news(url)
            if any(d in keywords for d in newtaipei_districts):
                print(f"✅ 處理新聞：{title}")
                cctv_list = match_cctv_for_keywords(keywords)
                generate_map_with_sidebar(
                    keywords, cctv_list, title, url, news_img, summary, timestamp
                )
                count += 1
        except Exception as e:
            print(f"⚠️ 解析失敗：{e}")

    print(f"🎯 成功處理 {count} 則新北市新聞")

    # ---------- 產生首頁 index.html ----------
    print("🧾 產生首頁 index.html...")
    generate_index_html()

    # ---------- Git 操作 ----------
    print("⬆️ 推送更新到 GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"🔄 自動更新 index 與 metadata"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "gh-pages"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作錯誤：{e}")
    print("✅ 全部完成！請查看 GitHub 網頁發布頁面。")


if __name__ == "__main__":
    run_all()
