import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートの設定
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def check_db():
    db_path_raw = os.getenv("DATABASE_PATH")
    if not db_path_raw:
        print("エラー: DATABASE_PATH が設定されていません。")
        return
        
    db_path = BASE_DIR / db_path_raw
    
    print(f"{'='*60}")
    print(f" POM Database Inspection Report (Unified Version)")
    print(f"{'='*60}")
    print(f"Target Path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. スキーマバージョンの確認
        print(f"\n[System Information]")
        try:
            cursor.execute("SELECT value FROM meta_info WHERE key='schema_version'")
            version = cursor.fetchone()
            print(f" - Schema Version: {version['value'] if version else 'Unknown'}")
        except Exception:
            print(" - Schema Version: meta_info table not found or version not set")

        # 2. テーブル一覧と詳細構造の取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        for table_name in tables:
            print(f"\n[Table: {table_name}]")
            
            # レコード件数の取得
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            total_count = cursor.fetchone()['count']
            print(f" - Total Records: {total_count} rows")
            
            # messagesテーブルの場合は方向別の内訳を表示
            if table_name == "messages":
                cursor.execute("SELECT direction, COUNT(*) as count FROM messages GROUP BY direction")
                directions = cursor.fetchall()
                for d in directions:
                    print(f"   - {d['direction']}: {d['count']} rows")
            
            # カラム情報の取得
            print(f" - Columns Structure:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            for col in cursor.fetchall():
                pk_mark = "[PK]" if col['pk'] else "    "
                print(f"    {pk_mark} {col['name']:<16} | {col['type']:<8} | NotNull: {col['notnull']}")

        # 3. インデックス情報の取得
        print(f"\n{'='*60}")
        print(f" Index Information")
        print(f"{'='*60}")
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = cursor.fetchall()
        if indexes:
            for idx in indexes:
                print(f" - Index: {idx['name']:<25} (on Table: {idx['tbl_name']})")
        else:
            print(" - No custom indexes found.")
            
        conn.close()
        print(f"\n{'='*60}")
        print(f" Inspection Completed Successfully")
        
    except Exception as e:
        print(f"An unexpected error occurred during inspection: {e}")

if __name__ == "__main__":
    check_db()