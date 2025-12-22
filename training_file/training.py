# 安裝 YOLOv8/v11 的官方函式庫
#!pip install ultralytics
#!pip install roboflow
#!pip install fastapi
#!pip install uvicorn
#!pip install line-bot-sdk
#!pip install opencv-python
#!pip install requests

from ultralytics import YOLO
import os

from roboflow import Roboflow
rf = Roboflow(api_key="TVWOpsqkNmDwCcK5CMb1")
project = rf.workspace("ps-workspace-c1emr").project("food-recognition-79wbi")
version = project.version(1)
dataset = version.download("yolov8")

# 載入預訓練權重
model = YOLO('yolov8n.pt')

# 開始訓練
results = model.train(
    data=f"{dataset.location}/data.yaml", # 資料設定檔路徑
    epochs=50,                           # 訓練 50 輪 (可視情況增加)
    imgsz=640,                           # 圖片縮放到 640x640
    plots=True                           # 輸出訓練圖表
)
