import os
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートの設定
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def dump_db():
    db_path_raw = os.getenv("DATABASE_PATH")
    if not db_path_raw:
        print("エラー: DATABASE_PATH が設定されていません。")
        return
        
    db_path = BASE_DIR / db_path_raw
    if not os.path.exists(db_path):
        print(f"エラー: {db_path} が存在しません。")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 統合された単一のテーブルを対象にします
        table_name = "messages"

        print(f"\n{'='*100}")
        print(f" DATABASE DUMP: {table_name.upper()} (Unified Schema v2.0)")
        print(f"{'='*100}")
        # 見出しに DIR (方向) を追加
        print(f"{'UIDL':<15} | {'DIR':<8} | {'STATUS':<15} | {'CONTACT':<20} | {'SUBJECT':<30}")
        print(f"{'-'*100}")

        # 統合テーブルから全件取得
        query = f"SELECT uidl, direction, contact_address, subject, status, body_text FROM {table_name} ORDER BY sent_at DESC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            # 表示幅に合わせて各項目を調整
            uidl_display = (row['uidl'][:12] + '..') if len(row['uidl']) > 12 else row['uidl']
            
            # 方向の表示 (inbound -> IN, outbound -> OUT)
            dir_display = "IN" if row['direction'] == 'inbound' else "OUT"
            
            # JSON形式のステータスを読みやすく整形 ( ["a", "b"] -> A, B )
            try:
                status_list = json.loads(row['status'])
                status_text = ", ".join(status_list).upper()
            except:
                status_text = str(row['status']).upper()
            
            status_display = (status_text[:13] + '..') if len(status_text) > 13 else status_text
            contact = (row['contact_address'][:18] + '..') if len(row['contact_address']) > 18 else row['contact_address']
            subject = (row['subject'][:27] + '..') if row['subject'] and len(row['subject']) > 27 else (row['subject'] or "")
            
            print(f"{uidl_display:<15} | {dir_display:<8} | {status_display:<15} | {contact:<20} | {subject:<30}")
            
            # 本文のプレビュー表示
            body_preview = (row['body_text'] or "").replace('\n', ' ')[:90]
            print(f"  Preview: {body_preview}...")
            print(f"{'-'*100}")

        if not rows:
            print("  表示できるデータが存在しません。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    dump_db()