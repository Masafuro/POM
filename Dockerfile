FROM python:3.11-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコンテナにコピー
COPY . .

# 標準出力がバッファリングされないように設定（ログをリアルタイムで見るため）
ENV PYTHONUNBUFFERED=1

# プログラムを実行
CMD ["python", "main.py"]