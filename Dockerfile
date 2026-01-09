# 使用輕量級 Python 影像
FROM python:3.9-slim

# 安裝系統必要的 lib (YOLO 辨識 opencv 需要用到)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製檔案
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼 (包含 models 夾)
COPY . .

# 啟動指令 (使用 $PORT 變數)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT