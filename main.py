from fastapi import FastAPI, Request, BackgroundTasks
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
import os
import uuid
from model_handler import FoodInference
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
print(f"Token 長度: {len(os.getenv('LINE_CHANNEL_ACCESS_TOKEN') or '')}")

def log_meal(food_name, calories):
    file_exists = os.path.isfile('diet_logs.csv')
    with open('diet_logs.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 如果是新檔案，先寫入標題
        if not file_exists:
            writer.writerow(['時間', '食物名稱', '熱量(kcal)'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), food_name, calories])

app = FastAPI()

# 填入你的金鑰
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化辨識器
inference = FoodInference()

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    handler.handle(body.decode(), signature)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 1. 幫圖片取個臨時名字
    file_path = f"temp_{uuid.uuid4()}.jpg"
    
    # 2. 下載 Line 伺服器上的圖片
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # 3. 執行辨識
    result = inference.analyze(file_path)
    
    # 暫時的回覆邏輯
    reply = "圖片已收到！AI 正在辨識中..."
    
    if result["success"]:
        # 紀錄飲食
        log_meal(result['name'], result['calories'])
        
        # 組合回覆內容
        reply = (f"🔍 辨識成功：{result['name']}\n"
                 f"🔥 熱量：{result['calories']} kcal/{result['unit']}\n"
                 f"📊 營養：{result['nutrition']}\n"
                 f"✨ 信心度：{result['conf']}\n\n"
                 f"✅ 已為您存入飲食日誌！")
    else:
        reply = "抱歉，目前我認不出這個食物，我會再努力學習的！😢"
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    
    # 4. 刪除暫存圖
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)