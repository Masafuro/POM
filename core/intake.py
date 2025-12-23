import os
import poplib
import sqlite3
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from dotenv import load_dotenv

load_dotenv()

def decode_mime_header(s):
    """メールヘッダー（件名など）を適切にデコードする"""
    if not s:
        return ""
    decoded_list = decode_header(s)
    header_parts = []
    for content, charset in decoded_list:
        if isinstance(content, bytes):
            header_parts.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            header_parts.append(content)
    return "".join(header_parts)

def get_email_content(msg):
    """メールオブジェクトから本文(text/html)を抽出する"""
    body_text = ""
    body_html = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            charset = part.get_content_charset() or "utf-8"
            
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                decoded_payload = payload.decode(charset, errors="replace")
                
                if content_type == "text/plain":
                    body_text += decoded_payload
                elif content_type == "text/html":
                    body_html += decoded_payload
            except:
                continue
    else:
        charset = msg.get_content_charset() or "utf-8"
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                decoded_payload = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    body_html = decoded_payload
                else:
                    body_text = decoded_payload
        except:
            pass
            
    return body_text, body_html

def intake():
    db_path = os.getenv("DATABASE_PATH", "data/pom.db")
    # main.py の環境変数名に合わせる
    host = os.getenv("MAIL_SERVER")
    user = os.getenv("MAIL_USER")
    password = os.getenv("MAIL_PASS")
    port = int(os.getenv("MAIL_PORT", 995))

    if not host or not user or not password:
        print("Error: Mail configuration is missing in .env")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Connecting to {host} as {user}...")
    server = poplib.POP3_SSL(host, port)
    server.user(user)
    server.pass_(password)

    try:
        # UIDLの一覧を取得
        _, items, _ = server.uidl()
        uidls = [item.decode().split() for item in items]

        for msg_num, uidl in uidls:
            # 既にDBに存在するUIDLはスキップ
            cursor.execute("SELECT 1 FROM emails WHERE uidl = ?", (uidl,))
            if cursor.fetchone():
                continue

            print(f"Fetching new email (UIDL: {uidl})...")
            _, lines, _ = server.retr(msg_num)
            raw_content = b"\r\n".join(lines)
            msg = message_from_bytes(raw_content)

            # ヘッダー情報の解析（デコード処理付き）
            subject = decode_mime_header(msg.get("Subject", "(No Subject)"))
            from_header = decode_mime_header(msg.get("From", ""))
            sender_name, sender_address = parseaddr(from_header)
            
            # 日時の正規化
            date_header = msg.get("Date")
            sent_at = None
            if date_header:
                try:
                    sent_at = parsedate_to_datetime(date_header).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

            # 本文の分離
            body_text, body_html = get_email_content(msg)

            # データベースへの保存
            cursor.execute("""
                INSERT INTO emails (
                    uidl, sender_name, sender_address, subject, 
                    body_text, body_html, sent_at, raw_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uidl, sender_name, sender_address, subject, 
                body_text, body_html, sent_at, raw_content.decode(errors="replace")
            ))
            conn.commit()
            print(f"Stored: {subject}")

    finally:
        server.quit()
        conn.close()
        print("Intake process finished.")

if __name__ == "__main__":
    intake()