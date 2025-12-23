FROM python:3.11-slim

WORKDIR /app

# まず requirements.txt をコピーし、pip install を実行する
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# その後に残りのソースコードをコピーする
COPY . .

CMD ["python", "main.py"]