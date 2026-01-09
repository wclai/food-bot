import json
import logging
from ultralytics import YOLO

# 設定日誌，方便在 GCP Logs 查看進度
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodInference:
    def __init__(self, model_path='models/best.pt', data_path='food_data.json'):
        logger.info("正在初始化 YOLO 模型與資料庫...")
        # 載入模型
        self.model = YOLO(model_path)
        # 載入營養資料
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.food_db = json.load(f)
        except Exception as e:
            logger.error(f"無法載入資料庫: {e}")
            self.food_db = {}
        logger.info("初始化完成。")

    def analyze(self, image_path):
        # 增加 half=True 優化效能
        results = self.model.predict(source=image_path, conf=0.4, half=False) # Cloud Run CPU 建議先維持 False 避免相容問題
        
        if len(results[0].boxes) > 0:
            # 取得標籤名稱
            label = self.model.names[int(results[0].boxes[0].cls[0])]
            confidence = float(results[0].boxes[0].conf[0])
            
            # 查表
            info = self.food_db.get(label, None)
            if info:
                return {
                    "success": True,
                    "name": info['name'],
                    "calories": info['calories'],
                    "nutrition": f"P:{info.get('protein',0)}g / F:{info.get('fat',0)}g / C:{info.get('carbs',0)}g",
                    "unit": info['unit'],
                    "conf": f"{confidence:.2%}"
                }
        
        return {"success": False}

# --- 重要：在模組層級建立單例 (Singleton) ---
# 這樣 main.py 匯入時就會直接初始化一次
food_inference = FoodInference()