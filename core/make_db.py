import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# SQLスキーマ定義
SCHEMA = """
CREATE TABLE IF NOT EXISTS emails (
    uidl TEXT PRIMARY KEY,
    subject TEXT,
    sender TEXT,
    body TEXT,
    raw_source TEXT,
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meta_info (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON emails(status);
"""

def init_db():
    """
    .env の設定に基づいてデータベースを初期化する。
    """
    # .env からデータベースのパスを取得。設定がない場合はデフォルト値を使用。
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    
    # 1. 保存先ディレクトリの作成
    db_dir = Path(db_path).parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

    # 2. SQLiteへの接続とテーブル構築
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(SCHEMA)
        
        # 初期メタデータの登録
        cursor.execute("INSERT OR IGNORE INTO meta_info (key, value) VALUES ('schema_version', '1.0')")
        
        conn.commit()
        print(f"データベースの初期化が完了しました: {db_path}")
        
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    # 直接実行された場合は、設定に基づいてDBを構築する
    init_db()