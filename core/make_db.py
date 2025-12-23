import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 分離格納を前提としたテーブル定義
TABLES = {
"emails": """
        CREATE TABLE IF NOT EXISTS emails (
            uidl TEXT PRIMARY KEY,
            sender_name TEXT,
            sender_address TEXT,
            subject TEXT,
            body_text TEXT,
            body_html TEXT,
            sent_at DATETIME,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 0,    -- 処理ステータス（業務ロジック用）
            is_new INTEGER DEFAULT 1,     -- 新着フラグ（システムサイクル用）
            is_read INTEGER DEFAULT 0,    -- 既読フラグ（UI/人間用：将来のため追加）
            raw_source TEXT
        );
    """,
    "meta_info": """
        CREATE TABLE IF NOT EXISTS meta_info (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """
}

# 検索の高速化とデータの整合性を支えるインデックス定義
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status);",
    "CREATE INDEX IF NOT EXISTS idx_emails_is_new ON emails(is_new);",
    "CREATE INDEX IF NOT EXISTS idx_emails_is_read ON emails(is_read);",
    "CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at);"
]

def init_db():
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    
    # 保存先ディレクトリの存在確認と作成
    db_dir = Path(db_path).parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {db_dir}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 各テーブルの作成
        for table_name, sql in TABLES.items():
            cursor.execute(sql)
            print(f"Table verified/created: {table_name}")
        
        # 2. インデックスの作成
        for idx_sql in INDEXES:
            cursor.execute(idx_sql)
            print("Index verified/created.")
        
        # 3. 初期メタデータの登録
        cursor.execute("INSERT OR IGNORE INTO meta_info (key, value) VALUES ('schema_version', '1.0')")
        
        conn.commit()
        print(f"\nデータベースの初期化が正常に完了しました: {db_path}")
        
    except sqlite3.Error as e:
        print(f"\nSQLiteエラーが発生しました: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_db()