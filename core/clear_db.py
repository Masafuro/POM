import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートの設定
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def clear_db():
    db_path_raw = os.getenv("DATABASE_PATH")
    if not db_path_raw:
        print("エラー: .env ファイルで DATABASE_PATH が設定されていません。")
        return

    db_path = BASE_DIR / db_path_raw
    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return

    print(f"警告: {db_path} 内のメッセージデータを削除します。")
    print("※システム設定（meta_info）は保持されます。")
    confirm = input("本当によろしいですか？ (y/n): ")
    if confirm.lower() != 'y':
        print("処理を中断しました。")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 動的にテーブル名を取得しますが、meta_info テーブルは除外します
        # これにより、スキーマバージョンなどの重要な設定情報を保護します
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # 削除対象から meta_info を取り除いたリストを作成
        target_tables = [t for t in all_tables if t != 'meta_info']

        for table_name in target_tables:
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"データを消去しました: {table_name}")

        # sqlite_sequenceテーブルが存在する場合のみ、カウンタをリセット
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';")
        if cursor.fetchone():
            cursor.execute("DELETE FROM sqlite_sequence;")
            print("オートインクリメントのカウンタをリセットしました。")

        conn.commit()
        
        # 物理的なファイルサイズを削減し、データベースを最適化
        cursor.execute("VACUUM;")
        print("データベースの最適化（VACUUM）が完了しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("データベース接続を閉じました。")

if __name__ == "__main__":
    clear_db()