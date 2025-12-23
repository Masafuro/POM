import os
import sqlite3
from dotenv import load_dotenv

def check_db():
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    
    print(f"{'='*50}")
    print(f" POM Database Inspection Report")
    print(f"{'='*50}")
    print(f"Target Path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得
        cursor = conn.cursor()
        
        # 1. テーブル一覧と各テーブルの詳細構造を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        for table_name in tables:
            print(f"\n[Table: {table_name}]")
            
            # レコード件数の取得
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f" - Records: {count} rows")
            
            # カラム情報の取得 (CID, Name, Type, NotNull, DefaultValue, PK)
            print(f" - Columns:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            for col in cursor.fetchall():
                pk_mark = "[PK]" if col['pk'] else "    "
                print(f"   {pk_mark} {col['name']:<12} | {col['type']:<8} | NotNull: {col['notnull']}")

        # 2. インデックス情報の取得
        print(f"\n{'='*50}")
        print(f" Index Information")
        print(f"{'='*50}")
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f" - Index: {idx['name']} (on Table: {idx['tbl_name']})")
            
        conn.close()
        print(f"\n{'='*50}")
        print(f" Inspection Completed")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_db()