import os
import sqlite3
from dotenv import load_dotenv

def dump_db():
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} does not exist.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n{'='*80}")
    print(f"{'UIDL':<20} | {'SENDER':<25} | {'SUBJECT':<30}")
    print(f"{'-'*80}")

    try:
        cursor.execute("SELECT uidl, sender_address, subject, body_text FROM emails;")
        rows = cursor.fetchall()
        
        for row in rows:
            # 表示用に文字列を短くカット
            uidl_short = (row['uidl'][:17] + '..') if len(row['uidl']) > 17 else row['uidl']
            subject = (row['subject'][:27] + '..') if len(row['subject']) > 27 else row['subject']
            sender = (row['sender_address'][:22] + '..') if len(row['sender_address']) > 22 else row['sender_address']
            
            print(f"{uidl_short:<20} | {sender:<25} | {subject:<30}")
            
            # 本文も少しだけ表示
            body_preview = row['body_text'].replace('\n', ' ')[:75]
            print(f"  Content: {body_preview}...")
            print(f"{'-'*80}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    dump_db()