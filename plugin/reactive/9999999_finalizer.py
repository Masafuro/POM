# reactive/99999_finalizer.py
import sqlite3
import os
from dotenv import load_dotenv

# .envファイルを読み込むようにしておくと、単体実行時も安心です
load_dotenv()

def finalize():
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 今回の新着分をシステム処理済みに更新
    cursor.execute("UPDATE emails SET is_processed = 1 WHERE is_new = 1")
    updated_count = cursor.rowcount  # 更新された件数を取得
    
    conn.commit()
    conn.close()
    
    if updated_count > 0:
        print(f"Finalized: {updated_count} emails marked as processed (is_processed=1).")
    else:
        print("Finalized: No new emails to process.")

if __name__ == "__main__":
    finalize()