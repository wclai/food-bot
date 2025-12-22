# 🍜 台灣小吃 AI 營養師 Line Bot

這是一個結合 **YOLOv8 物件偵測技術** 與 **Line Messaging API** 的智慧機器人。使用者只需上傳台灣常見小吃的照片，機器人即可自動辨識食物種類，並提供即時的熱量估計與營養成分建議。

## 🌟 核心功能
* **食物辨識**：支援 15 種台灣常見小吃（如滷肉飯、牛肉麵、肉圓等）。
* **營養分析**：串接食藥署數據，提供熱量 (kcal)、蛋白質、脂肪及碳水化合物資訊。
* **飲食建議**：根據辨識結果給予健康的飲食小叮嚀。
* **飲食日誌**：自動記錄使用者的攝取紀錄於 `diet_logs.csv`。

## 🛠 技術棧
* **AI 模型**: YOLOv8 (Ultralytics)
* **後端框架**: FastAPI
* **開發語言**: Python 3.11+
* **資料來源**: 台灣食藥署 (FDA) 食品營養成分資料庫
* **部署工具**: Ngrok (本地測試)

## 📂 專案結構
```text
├── main.py              # Line Bot 主程式與 Webhook 邏輯
├── model_handler.py     # YOLO 模型推論與數據對照
├── food_data.json       # 食物營養成分資料庫
├── models/
│   └── best.pt          # 訓練好的 YOLOv8 模型權重 (需自行放入)
├── diet_logs.csv        # 系統自動生成的飲食紀錄
├── .env                 # 環境變數 (金鑰)
└── .gitignore           # 排除敏感檔案與模型
🚀 快速開始
1. 安裝依賴套件
Bash

pip install -r requirements.txt
(請確保已安裝 fastapi, uvicorn, line-bot-sdk, ultralytics, python-dotenv)

2. 設定環境變數
建立 .env 檔案並填入你的 Line Channel 資訊：

Plaintext

LINE_CHANNEL_ACCESS_TOKEN=你的AccessToken
LINE_CHANNEL_SECRET=你的ChannelSecret
3. 置入模型
將在 Google Colab 訓練完成的 best.pt 檔案放入 models/ 資料夾中。

4. 啟動服務
Bash

# 啟動 FastAPI
uvicorn main:app --reload

# 同時啟動 ngrok (如果是在本地開發)
ngrok http 8000
📊 辨識標籤清單 (Supported Classes)
本模型目前支援以下 15 種標籤： bawan, beef_noodles, braised_napa_cabbage, braised_pork_over_rice, chicken_mushroom_soup, chinese_pickled_cucumber, cold_noodle, deep-fried_chicken_cutlets, egg_pancake_roll, fried_instant_noodles, fried_rice_noodles, fried-spanish_mackerel_thick_soup, loofah, Over-easy egg, turkey_rice

📝 免責聲明
本專案提供之營養數據僅供參考，實際熱量可能因烹飪方式與份量大小而異。


---

### **接下來的操作建議**

1. **建立 `requirements.txt`**：
   為了讓這份 README 更完整，你可以在終端機執行 `pip freeze > requirements.txt`，這樣別人才知道要安裝哪些套件（或者你可以手動建立這個檔案，寫入我上面提到的那幾個主要套件）。

2. **上傳至 GitHub**：
   ```bash
   git add README.md
   git commit -m "Add professional README"
   git push origin main