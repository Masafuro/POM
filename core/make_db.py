import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートの設定
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"致命的なエラー: .env ファイルが {ENV_PATH} に見つかりません。")

load_dotenv(ENV_PATH)

# テーブル定義の統合
# 受信と送信をmessagesテーブルに一本化し、directionカラムで識別します
TABLES = {
    "messages": """
        CREATE TABLE IF NOT EXISTS messages (
            uidl TEXT PRIMARY KEY,
            direction TEXT NOT NULL, -- 'inbound' (受信) または 'outbound' (送信)
            contact_name TEXT,
            contact_address TEXT NOT NULL,
            subject TEXT,
            body_text TEXT,
            body_html TEXT,
            sent_at DATETIME,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT '[]', -- JSON配列形式でのタグ管理
            meta TEXT DEFAULT '{}',   -- JSON形式で返信先UIDLやエラー情報などを保持
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

# 統合テーブルに最適化したインデックス設定
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);",
    "CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_address);",
    "CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);"
]

def init_db():
    db_path_raw = os.getenv("DATABASE_PATH")
    if db_path_raw is None:
        raise KeyError("致命的なエラー: .env 内で DATABASE_PATH が定義されていません。")
    
    db_path = BASE_DIR / db_path_raw
    db_dir = db_path.parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # テーブルの作成
        for table_name, sql in TABLES.items():
            cursor.execute(sql)
            
        # インデックスの作成
        for idx_sql in INDEXES:
            cursor.execute(idx_sql)
        
        # スキーマバージョンを統合版を示す2.0に更新
        cursor.execute("INSERT OR IGNORE INTO meta_info (key, value) VALUES ('schema_version', '2.0')")
        cursor.execute("UPDATE meta_info SET value = '2.0' WHERE key = 'schema_version'")
        
        conn.commit()
        print(f"データベースの初期化に成功しました（メッセージ統合版）: {db_path}")
        
    except Exception as e:
        print(f"初期化中にエラーが発生しました: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_db()