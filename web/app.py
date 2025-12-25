import os
import sqlite3
import uuid
import json
from pathlib import Path
from flask import Flask, render_template, abort, request, jsonify
from dotenv import load_dotenv
from flask_mail import Mail, Message

# プロジェクトルートのパス設定
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SMTPサーバーの設定
app.config['MAIL_SERVER'] = os.getenv("SMTP_HOST")
app.config['MAIL_PORT'] = int(os.getenv("SMTP_PORT", "587"))
app.config['MAIL_USE_TLS'] = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
app.config['MAIL_USERNAME'] = os.getenv("SMTP_USER")
app.config['MAIL_PASSWORD'] = os.getenv("SMTP_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("SMTP_USER")

mail = Mail(app)

def get_db_connection():
    db_path_raw = os.getenv("DATABASE_PATH")
    db_path = BASE_DIR / db_path_raw
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        # 単一の messages テーブルから JSON 内のタグをバラバラに展開して集計します
        query = '''
            SELECT value as tag, count(*) as count
            FROM messages, json_each(status)
            GROUP BY tag
            ORDER BY count DESC
        '''
        tags = conn.execute(query).fetchall()
        conn.close()
        return render_template('index.html', tags=tags)
    except Exception:
        # データベースが空の状態や初期化前でもエラーにならないよう空のリストを返します
        return render_template('index.html', tags=[])

@app.route('/list/<category>')
def list_emails(category):
    try:
        conn = get_db_connection()
        # 表示するページのタイトルを管理するためのマッピング
        titles = {'inbox': '受信一覧', 'sent': '送信済み一覧', 'new': '新着メール'}
        title = titles.get(category, f"タグ: {category}")

        # 指定されたカテゴリ名（タグ）が JSON 配列内に含まれているレコードを単一テーブルから抽出
        query = '''
            SELECT *
            FROM messages, json_each(messages.status)
            WHERE json_each.value = ?
            ORDER BY sent_at DESC LIMIT 100
        '''
        emails = conn.execute(query, (category,)).fetchall()
        
        conn.close()
        return render_template('list.html', emails=emails, title=title, category=category)
    except Exception as e:
        return f"データベースエラーが発生しました: {str(e)}", 500

@app.route('/email/<uidl>')
def detail(uidl):
    conn = get_db_connection()
    # テーブルが一つになったため、検索も一回で完結します
    email = conn.execute('SELECT * FROM messages WHERE uidl = ?', (uidl,)).fetchone()
    conn.close()
    if not email:
        abort(404)
    return render_template('detail.html', email=email)

@app.route('/send', methods=['POST'])
def send_email():
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    body = request.form.get('body')
    new_uidl = f"SENT-{uuid.uuid4().hex[:12].upper()}"
    
    # 送信済みメッセージとして方向（direction）と初期タグ（status）を設定
    initial_status = json.dumps(["sent"])
    
    msg = Message(subject=subject, recipients=[recipient], body=body)
    try:
        mail.send(msg)
        conn = get_db_connection()
        # 統合テーブル messages へ direction='outbound' として保存
        conn.execute('''
            INSERT INTO messages (uidl, direction, contact_address, subject, body_text, status) 
            VALUES (?, 'outbound', ?, ?, ?, ?)
        ''', (new_uidl, recipient, subject, body, initial_status))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "送信が正常に完了しました。", "uidl": new_uidl})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)