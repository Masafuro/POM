import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# coreディレクトリ内にあるため、二段階上がプロジェクトルートです
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    raise FileNotFoundError(f"致命的なエラー: .env ファイルが {ENV_PATH} に見つかりません。")

load_dotenv(ENV_PATH)

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
            status INTEGER DEFAULT 0,
            is_new INTEGER DEFAULT 1,
            is_processed INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            raw_source TEXT
        );
    """,
    "sent_emails": """
        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_address TEXT,
            recipient_address TEXT NOT NULL,
            subject TEXT,
            body_text TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reply_to_uidl TEXT,
            status TEXT DEFAULT 'sent',
            error_message TEXT,
            FOREIGN KEY (reply_to_uidl) REFERENCES emails (uidl)
        );
    """,
    "meta_info": """
        CREATE TABLE IF NOT EXISTS meta_info (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status);",
    "CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_sent_emails_sender ON sent_emails(sender_address);",
    "CREATE INDEX IF NOT EXISTS idx_sent_emails_sent_at ON sent_emails(sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_sent_emails_reply_to ON sent_emails(reply_to_uidl);"
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
        for table_name, sql in TABLES.items():
            cursor.execute(sql)
        for idx_sql in INDEXES:
            cursor.execute(idx_sql)
        cursor.execute("INSERT OR IGNORE INTO meta_info (key, value) VALUES ('schema_version', '1.2')")
        conn.commit()
        print(f"データベースの初期化に成功しました: {db_path}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_db()