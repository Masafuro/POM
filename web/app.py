import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, abort, request, jsonify
from dotenv import load_dotenv
from flask_mail import Mail, Message

# web/app.py の二段階上がルートです
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SMTP設定（新しい変数名に準拠）
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
    return render_template('index.html')

@app.route('/list/<category>')
def list_emails(category):
    try:
        conn = get_db_connection()
        if category == 'inbox':
            emails = conn.execute('SELECT * FROM emails ORDER BY sent_at DESC LIMIT 100').fetchall()
            title = "受信一覧"
        elif category == 'sent':
            emails = conn.execute('SELECT id AS uidl, sent_at, recipient_address AS sender_name, subject, status FROM sent_emails ORDER BY sent_at DESC LIMIT 100').fetchall()
            title = "送信済み一覧"
        else: abort(404)
        conn.close()
        return render_template('list.html', emails=emails, title=title, category=category)
    except Exception as e: return f"データベースエラー: {str(e)}", 500

@app.route('/email/<uidl>')
def detail(uidl):
    conn = get_db_connection()
    email = conn.execute('SELECT * FROM emails WHERE uidl = ?', (uidl,)).fetchone()
    conn.close()
    if not email: abort(404)
    return render_template('detail.html', email=email)

@app.route('/send', methods=['POST'])
def send_email():
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    body = request.form.get('body')
    msg = Message(subject=subject, recipients=[recipient], body=body)
    try:
        mail.send(msg)
        conn = get_db_connection()
        conn.execute('INSERT INTO sent_emails (sender_address, recipient_address, subject, body_text, status) VALUES (?, ?, ?, ?, ?)',
                     (app.config['MAIL_USERNAME'], recipient, subject, body, 'sent'))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "送信完了しました。"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)