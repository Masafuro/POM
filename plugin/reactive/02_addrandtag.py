import os
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv

# プラグインの配置場所（/app/plugin/reactive/）から三段階上をルートディレクトリとして特定します
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# .envファイルを読み込み、設定情報を取得します
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(Path.cwd() / ".env")

def auto_tagging():
    db_path_raw = os.getenv("DATABASE_PATH")
    if not db_path_raw:
        print("エラー: DATABASE_PATH が設定されていません。")
        return
        
    # データベースへの絶対パスを構築し、ファイルの存在を確認します
    db_path = BASE_DIR / db_path_raw
    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 統合テーブル「messages」から、受信したばかりの新着メッセージ（["new"]）を取得します
        # 送信済みメッセージを誤って処理しないよう direction を指定するのがポイントです
        cursor.execute("""
            SELECT uidl FROM messages 
            WHERE direction = 'inbound' AND status = '["new"]' 
            ORDER BY sent_at ASC;
        """)
        new_emails = cursor.fetchall()

        if not new_emails:
            print("処理対象の新規メッセージはありませんでした。")
            return

        print(f"{len(new_emails)} 件の新規メッセージを処理します。")

        for i, row in enumerate(new_emails):
            uidl = row['uidl']
            # 今回のロジックでは inbox1 と inbox2 を交互に割り振ります
            tag = "inbox1" if i % 2 == 0 else "inbox2"
            new_status_json = json.dumps([tag])
            
            # messagesテーブルのstatusカラムを、JSON形式の新しいタグで更新します
            cursor.execute(
                "UPDATE messages SET status = ? WHERE uidl = ?",
                (new_status_json, uidl)
            )
            print(f"UIDL: {uidl} のステータスを '{tag}' に更新しました。")

        conn.commit()
        print("全てのタグ付け処理が正常に完了しました。")

    except Exception as e:
        print(f"タグ付け処理中にエラーが発生しました: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    auto_tagging()