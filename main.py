from fastapi import FastAPI, Request, BackgroundTasks
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, FlexSendMessage, 
    BubbleContainer, ImageComponent, BoxComponent, TextComponent, FillerComponent, 
    CameraAction, QuickReply, QuickReplyButton
)
import os
import uuid
from model_handler import FoodInference
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
print(f"Token 長度: {len(os.getenv('LINE_CHANNEL_ACCESS_TOKEN') or '')}")

app = FastAPI()

# 填入你的金鑰
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化辨識器
inference = FoodInference()

def log_meal(food_name, calories):
    file_exists = os.path.isfile('diet_logs.csv')
    with open('diet_logs.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 如果是新檔案，先寫入標題
        if not file_exists:
            writer.writerow(['時間', '食物名稱', '熱量(kcal)'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), food_name, calories])



def create_food_flex(food_name, calories, nutrition, conf, image_url):
    # 如果還沒有上傳圖片到雲端，image_url 可以先帶一個 placeholder
    # if not image_url.startswith("https"):
    #    image_url = "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80"

    flex_content = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          # 頂部點綴綠色裝飾條，取代空白圖片
          {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "height": "10px",
            "backgroundColor": "#1DB446",
            "margin": "none"
          },
          {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "contents": [
              {"type": "text", "text": "AI 營養分析報告", "weight": "bold", "color": "#1DB446", "size": "sm"},
              {"type": "text", "text": food_name, "weight": "bold", "size": "xl", "margin": "md"},
              {"type": "separator", "margin": "lg"},
              {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": [
                {
                  "type": "box", "layout": "baseline", "spacing": "sm", "contents": [
                    {"type": "text", "text": "預估熱量", "color": "#aaaaaa", "size": "sm", "flex": 2},
                    {"type": "text", "text": f"{calories} kcal", "wrap": True, "color": "#ee5253", "size": "sm", "flex": 4, "weight": "bold"}
                  ]
                },
                {
                  "type": "box", "layout": "baseline", "spacing": "sm", "contents": [
                    {"type": "text", "text": "營養組成", "color": "#aaaaaa", "size": "sm", "flex": 2},
                    {"type": "text", "text": nutrition, "wrap": True, "color": "#666666", "size": "sm", "flex": 4}
                  ]
                },
                {
                  "type": "box", "layout": "baseline", "spacing": "sm", "contents": [
                    {"type": "text", "text": "辨識信心", "color": "#aaaaaa", "size": "sm", "flex": 2},
                    {"type": "text", "text": conf, "wrap": True, "color": "#666666", "size": "sm", "flex": 4}
                  ]
                }
              ]}
            ]
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "style": "primary",
            "height": "sm",
            "color": "#1DB446",
            "action": {
              "type": "message",
              "label": "記入今日飲食",
              "text": f"確認紀錄：{food_name}"
            }
          },
          {
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "action": {
              "type": "message",
              "label": "查看今日總結",
              "text": "今日熱量總結"
            }
          }
        ]
      },
      "styles": {
        "footer": {"separator": True}
      }
    }
    return FlexSendMessage(alt_text=f"辨識結果：{food_name}", contents=flex_content)

def get_today_total():
    today = datetime.now().strftime("%Y-%m-%d")
    total_cal = 0
    if os.path.exists('diet_logs.csv'):
        with open('diet_logs.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 跳過標題
            for row in reader:
                if row[0].startswith(today):
                    total_cal += float(row[2])
    return total_cal

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    # 丟到背景執行，立刻回傳 200 給 Line
    background_tasks.add_task(handler.handle, body.decode(), signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage) # 確保這裡是 TextMessage
def handle_text(event):
    user_msg = event.message.text
    
    if user_msg == "今日熱量總結":
        total = get_today_total()
        reply_text = f"📊 今日攝取總結\n---\n總熱量：{total} kcal"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif user_msg == "/camera":
        # 這是選單左邊按鈕觸發的指令
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="請點擊下方按鈕開啟相機拍照：",
                           quick_reply=QuickReply(items=[
                               QuickReplyButton(action=CameraAction(label="開啟相機"))
                           ])))
  
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
        log_meal(result['name'], result['calories'])
        reply_content = create_food_flex(
            result['name'], 
            result['calories'], 
            result['nutrition'], 
            result['conf'],
            "https://i.imgur.com/placeholder.jpg" 
        )
    else:
        reply_content = TextSendMessage(text="抱歉，目前我認不出這個食物 😢")
    
    line_bot_api.reply_message(event.reply_token, reply_content)
    
    # 4. 刪除暫存圖
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)