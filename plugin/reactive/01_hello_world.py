import os
import sqlite3

def main():
    # .env や親プロセスから引き継いだ環境変数からDBパスを取得
    db_path = os.environ.get("DATABASE_PATH", "data/pom.db")
    
    print(f"--- [01_hello_world] 起動 ---")
    print(f"使用DBパス: {db_path}")
    
    # ここでは単純な動作確認のみを行います
    print("Hello, POM! Reactiveステージの逐次処理が正常に開始されました。")
    
    # 本来はここでSQLiteに接続し、新着メールを処理します
    # conn = sqlite3.connect(db_path)
    # ...ロジック...
    
    print(f"--- [01_hello_world] 完了 ---")

if __name__ == "__main__":
    main()