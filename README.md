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
        subject      | TEXT     | NotNull: 0
        sender       | TEXT     | NotNull: 0
        body         | TEXT     | NotNull: 0
        raw_source   | TEXT     | NotNull: 0
        received_at  | DATETIME | NotNull: 0
        status       | INTEGER  | NotNull: 0

[Table: meta_info]
 - Records: 1 rows
 - Columns:
   [PK] key          | TEXT     | NotNull: 0
        value        | TEXT     | NotNull: 0

==================================================
 Index Information
==================================================
 - Index: idx_status (on Table: emails)

==================================================
 Inspection Completed
```


## 実行規則
プラグインの実行規約
- plugins/reactive および plugins/scheduled 内のスクリプトは、以下の規則に従って自動実行されます。
- 実行順序: [数値]_[名前].py という形式のファイル名を作成してください。数値の小さい順に逐次実行されます（例: 01_parse.py -> 02_notify.py）。
- 除外設定: 先頭をアンダースコア（_）で始めたファイルは無視されます。共通処理の切り出し等に使用してください。
- 独立性: 各スクリプトは独立したプロセスとして起動します。共通のデータは SQLite を介してやり取りしてください。