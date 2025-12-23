# POM
VPS上に構築する、POPメールデータを起点としたシンプルなPython実行拠点。Programmable Open Mailbox (POM) のリファレンス実装。

## セットアップ
1. 環境変数の設定
.env.example をコピーして .env ファイルを作成し、必要な情報を記入してください。特に DATABASE_PATH は、データベースファイルを保存する任意のパス（例：data/pom.db）に設定してください。

> cp .env.example .env

2. データベースの初期化
システムを稼働させる前に、以下のコマンドを実行してSQLiteデータベースと必要なテーブルを構築してください。この操作は初回のみ必要です。
> docker-compose run --rm pom-app python core/make_db.py

3. データベースの確認
実行後、指定したパスに .db ファイルが生成されていれば準備完了です。
> docker-compose run --rm pom-app python core/check_db.py

でデータベースを確認できます。

実行例
```bash
==================================================
 POM Database Inspection Report
==================================================
Target Path: data/pom.db

[Table: emails]
 - Records: 0 rows
 - Columns:
   [PK] uidl         | TEXT     | NotNull: 0
        sender_name  | TEXT     | NotNull: 0
        sender_address | TEXT     | NotNull: 0
        subject      | TEXT     | NotNull: 0
        body_text    | TEXT     | NotNull: 0
        body_html    | TEXT     | NotNull: 0
        sent_at      | DATETIME | NotNull: 0
        received_at  | DATETIME | NotNull: 0
        status       | INTEGER  | NotNull: 0
        raw_source   | TEXT     | NotNull: 0

[Table: meta_info]
 - Records: 1 rows
 - Columns:
   [PK] key          | TEXT     | NotNull: 0
        value        | TEXT     | NotNull: 0

==================================================
 Index Information
==================================================
 - Index: idx_emails_status (on Table: emails)
 - Index: idx_emails_sent_at (on Table: emails)

==================================================
 Inspection Completed
```
4. メールの取り込み確認（インテーク）

設定されたPOP3サーバーに接続し、新着メールを確認します。UIDL（固有識別子）を用いて既読チェックを行うため、重複してデータが保存される心配はありません。取り込まれたメールは、差出人や本文、日時などが適切に分離された状態でデータベースに格納されます。
> docker-compose run --rm pom-app python core/intake.py

5. データベースの状態確認

データベースの健全性を確認するためのツールが二種類用意されています。
構造確認 (check_db.py): テーブルのカラム定義やインデックスの設定状況、および現在の総レコード数を確認できます。スキーマの変更が正しく反映されているかを検証する際に有用です。
内容確認 (dump_db.py): 実際に格納されたメールの件名や本文の冒頭部分を一覧表示します。文字化けの有無や、パース処理の結果をCUI上で即座に確認するために使用します。

> docker-compose run --rm pom-app python core/check_db.py
> docker-compose run --rm pom-app python core/dump_db.py


## 実行規則
プラグインの実行規約
- plugins/reactive および plugins/scheduled 内のスクリプトは、以下の規則に従って自動実行されます。
- 実行順序: [数値]_[名前].py という形式のファイル名を作成してください。数値の小さい順に逐次実行されます（例: 01_parse.py -> 02_notify.py）。
- 除外設定: 先頭をアンダースコア（_）で始めたファイルは無視されます。共通処理の切り出し等に使用してください。
- 独立性: 各スクリプトは独立したプロセスとして起動します。共通のデータは SQLite を介してやり取りしてください。