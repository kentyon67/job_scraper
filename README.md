# Job Scraper

Greenhouse求人ページを対象に、一覧取得・詳細取得・失敗URLの再試行・CSVデータセット生成まで行う Python 製CLIツールです。

## Features

- 求人一覧ページのHTML取得
- 一覧HTMLから求人URLを抽出
- 各求人詳細ページのHTML保存
- 元URLの対応ファイル保存
- 失敗URLのCSVログ記録
- 失敗URLの再取得
- 保存済みHTMLから求人情報を抽出してCSV生成
- `argparse` によるCLIサブコマンド実行
- `requests.Session` による通信設定の共通化
- `logging` による進行状況・エラー記録
- `pathlib` による安定したパス管理

## Project Structure

```text
job_scraper/
├─ src/
│  ├─ cli.py
│  ├─ fetch_list.py
│  ├─ fetch_detail.py
│  ├─ retry_failed.py
│  ├─ build_dataset.py
│  └─ utils.py
├─ data/
│  ├─ raw/
│  ├─ logs/
│  └─ output/
├─ requirements.txt
├─ .gitignore
└─ README.md
