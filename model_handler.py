import json
from ultralytics import YOLO

class FoodInference:
    def __init__(self, model_path='models/best.pt', data_path='food_data.json'):
        # 載入模型
        self.model = YOLO(model_path)
        # 載入營養資料
        with open(data_path, 'r', encoding='utf-8') as f:
            self.food_db = json.load(f)

    def analyze(self, image_path):
        results = self.model.predict(source=image_path, conf=0.4)
        
        # 假設我們取辨識到第一個、信心值最高的食物
        if len(results[0].boxes) > 0:
            # 取得標籤名稱 (例如 'braised_pork_over_rice')
            label = self.model.names[int(results[0].boxes[0].cls[0])]
            confidence = float(results[0].boxes[0].conf[0])
            
            # 查表
            info = self.food_db.get(label, None)
            if info:
                return {
                    "success": True,
                    "name": info['name'],
                    "calories": info['calories'],
                    "nutrition": f"P:{info['protein']}g / F:{info['fat']}g / C:{info['carbs']}g",
                    "unit": info['unit'],
                    "conf": f"{confidence:.2%}"
                }
        
        return {"success": False}