import subprocess

def step(title):
    print(f"\n=== {title} ===")

# 步驟 1: 自動爬 ETtoday 新北市新聞
step("步驟 1️⃣：開始爬 ETtoday 新聞")
subprocess.run(["python", "news_to_cctv_combo.py"], check=True)

# 步驟 2: 產出首頁 index.html
step("步驟 2️⃣：產出首頁 index.html")
subprocess.run(["python", "generate_index.py"], check=True)

# 步驟 3: 自動 commit 並 push 到 GitHub（排除 news_maps/）
step("步驟 3️⃣：推送更新到 GitHub")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "🔄 自動更新 index 與 metadata"], check=False)
subprocess.run(["git", "push", "-u", "origin", "gh-pages"], check=True)

print("\n✅ 全部完成！請查看 GitHub 網頁發布頁面。")
