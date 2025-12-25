import os
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv

# main.pyから呼び出される際の作業ディレクトリを考慮しつつ、プロジェクトルートを特定します
# plugin/reactive/ 階層に配置されることを想定し、三段階上をルートとします
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

def main():
    # 環境変数からデータベースのパスを取得し、絶対パスを構築します
    db_path_raw = os.getenv("DATABASE_PATH", "data/pom.db")
    db_path = BASE_DIR / db_path_raw
    
    print(f"--- [01_helloworld] 起動 ---")
    
    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return

    try:
        # データベースに接続し、最新のメッセージ情報を確認します
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 新着（["new"]）の受信メールが何件あるかを確認するクエリ
        # JSON形式のステータスをそのまま比較します
        cursor.execute(
            "SELECT COUNT(*) as count FROM messages WHERE direction = 'inbound' AND status = '[\"new\"]'"
        )
        new_count = cursor.fetchone()['count']
        
        print(f"現在の未処理新着メール数: {new_count}件")
        print("Hello, POM! 統合データベースへのアクセスとReactiveステージの実行が確認されました。")

        conn.close()
    except Exception as e:
        print(f"データベースアクセス中にエラーが発生しました: {e}")
    
    print(f"--- [01_helloworld] 完了 ---")

if __name__ == "__main__":
    main()