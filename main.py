import os
import time
import poplib
from email import parser

def check_mail():
    # 環境変数から接続情報を取得
    server = os.environ.get('MAIL_SERVER')
    user = os.environ.get('MAIL_USER')
    password = os.environ.get('MAIL_PASS')
    # print(f"{server},{user},{password}")
    print(f"{user}へ接続します。")

    try:
        # サーバーへ接続（SSL利用を想定）
        mailbox = poplib.POP3_SSL(server)
        mailbox.user(user)
        mailbox.pass_(password)

        # メール件数を確認
        num_messages = len(mailbox.list()[1])
        print(f"現在、{num_messages}通のメールがサーバーにあります。")

        if num_messages > 0:
            # 最新の1通を取得
            response, lines, octets = mailbox.retr(num_messages)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = parser.Parser().parsestr(msg_content)
            print(f"最新メールの件名: {msg['Subject']}")

        mailbox.quit()
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    interval = int(os.environ.get('POLLING_INTERVAL', 600))
    print("POM 実行拠点を開始します。")
    
    while True:
        check_mail()
        print(f"{interval}秒間待機します...")
        time.sleep(interval)