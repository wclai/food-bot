import requests
import json

def fetch_taiwan_food_data():
    # 這是台灣政府資料開放平台的 API 網址 (範例網址，需視政府最新公告而定)
    url = "https://data.gov.tw/api/v2/rest/dataset/8543" 
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 建立你的對應表
        food_mapping = {}
        for item in data['records']:
            # 以食物名稱作為 Key，方便模型辨識後直接查找
            name = item['食品名稱']
            food_mapping[name] = {
                "calories": item['熱量(kcal)'],
                "protein": item['粗蛋白(g)'],
                "fat": item['粗脂肪(g)'],
                "carbs": item['總碳水化合物(g)'],
                "fiber": item['膳食纖維(g)']
            }
            
        # 存成 JSON 檔供 Line Bot 使用
        with open('food_data.json', 'w', encoding='utf-8') as f:
            json.dump(food_mapping, f, ensure_ascii=False, indent=4)
            
        print("資料表已自動建立完成！")
        
    except Exception as e:
        print(f"抓取失敗: {e}")

fetch_taiwan_food_data()