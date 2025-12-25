import os
import poplib
import sqlite3
import json
from pathlib import Path
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from dotenv import load_dotenv

# プロジェクトルートの設定
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def decode_mime_header(s):
    if not s: return ""
    decoded_list = decode_header(s)
    header_parts = []
    for content, charset in decoded_list:
        if isinstance(content, bytes):
            header_parts.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            header_parts.append(content)
    return "".join(header_parts)

def get_email_content(msg):
    body_text, body_html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            charset = part.get_content_charset() or "utf-8"
            try:
                payload = part.get_payload(decode=True)
                if payload is None: continue
                decoded = payload.decode(charset, errors="replace")
                if content_type == "text/plain": body_text += decoded
                elif content_type == "text/html": body_html += decoded
            except: continue
    else:
        charset = msg.get_content_charset() or "utf-8"
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                decoded = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html": body_html = decoded
                else: body_text = decoded
        except: pass
    return body_text, body_html

def intake():
    db_path_raw = os.getenv("DATABASE_PATH")
    host = os.getenv("POP3_HOST")
    port_val = os.getenv("POP3_PORT", "995")
    user = os.getenv("POP3_USER")
    password = os.getenv("POP3_PASSWORD")

    if not all([host, user, password, db_path_raw]):
        print("エラー: POP3サーバーの設定が .env に不足しています。")
        return

    db_path = BASE_DIR / db_path_raw
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 統合テーブル「messages」において、前回のサイクルで残った受信済み 'new' を 'inbox' に移行
    # direction = 'inbound' の条件を付けることで、送信済みメッセージに影響を与えないようにします
    cursor.execute("""
        UPDATE messages 
        SET status = '["inbox"]' 
        WHERE direction = 'inbound' AND status = '["new"]'
    """)
    conn.commit()

    print(f"Connecting to POP3: {host} as {user}...")
    try:
        server = poplib.POP3_SSL(host, int(port_val))
        server.user(user)
        server.pass_(password)
        _, items, _ = server.uidl()
        uidls = [item.decode().split() for item in items]

        for msg_num, uidl in uidls:
            # 統合テーブル messages から重複を確認
            cursor.execute("SELECT 1 FROM messages WHERE uidl = ?", (uidl,))
            if cursor.fetchone(): continue

            _, lines, _ = server.retr(msg_num)
            raw_content = b"\r\n".join(lines)
            msg = message_from_bytes(raw_content)

            subject = decode_mime_header(msg.get("Subject", "(No Subject)"))
            from_header = decode_mime_header(msg.get("From", ""))
            contact_name, contact_address = parseaddr(from_header)
            
            date_header = msg.get("Date")
            sent_at = parsedate_to_datetime(date_header).strftime('%Y-%m-%d %H:%M:%S') if date_header else None
            body_text, body_html = get_email_content(msg)

            # 新規メールの初期ステータスと、方向性（inbound）を定義
            initial_status = json.dumps(["new"])
            cursor.execute("""
                INSERT INTO messages (
                    uidl, direction, contact_name, contact_address, subject, 
                    body_text, body_html, sent_at, status, raw_source
                )
                VALUES (?, 'inbound', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uidl, contact_name, contact_address, subject, 
                body_text, body_html, sent_at, initial_status, raw_content.decode(errors="replace")
            ))
            conn.commit()
            print(f"新規取得: {subject}")

        server.quit()
    except Exception as e:
        print(f"取り込み中にエラーが発生しました: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    intake()