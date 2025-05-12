# 使用一個標準的 Python 3.9 輕量級映像
# 適用於大多數基於 x86-64 架構的 Linux 電腦
FROM python:3.9-slim-buster

# 設定環境變量，防止在安裝套件時出現互動提示
ENV DEBIAN_FRONTEND=noninteractive

# 設定工作目錄
WORKDIR /app

# === 更新系統套件並安裝時區數據 ===
# 使用 apt-get 更新套件列表並升級已安裝的套件
# 安裝 tzdata 套件以設定時區
# 清理 apt 快取以減小映像大小
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設定容器的時區為台灣標準時間 (Asia/Taipei)
ENV TZ=Asia/Taipei
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# === 安裝 Python 依賴 ===
# 將 requirements.txt 複製到工作目錄
COPY requirements.txt .

# 安裝 Python 依賴
# --no-cache-dir 可以減少映像大小
RUN pip install --no-cache-dir -r requirements.txt

# === 複製 Bot 程式碼 ===
# 將所有本地檔案 (除了 .dockerignore 中指定的) 複製到工作目錄
COPY . .

# === 設定容器啟動命令 ===
# 定義當容器啟動時要執行的命令
CMD ["python", "taiex_tracker.py"]