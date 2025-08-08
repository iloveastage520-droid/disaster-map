import subprocess
import os

base_folder = os.path.dirname(os.path.abspath(__file__))

combo_script = os.path.join(base_folder, "news_to_cctv_combo.py")
index_script = os.path.join(base_folder, "generate_index.py")

# 步驟 1：執行爬新聞並產地圖
print("🚀 執行新聞爬蟲與地圖產出...")
subprocess.run(["python", combo_script])

# 步驟 2：產首頁 index.html
print("🛠️ 產出首頁 index.html...")
subprocess.run(["python", index_script])

# 步驟 3：上傳到 GitHub
print("⬆️ 推送更新到 GitHub...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "自動更新地圖與首頁"])
subprocess.run(["git", "push", "origin", "gh-pages"])

print("✅ 全部完成！請查看 GitHub 網頁發布頁面。")
