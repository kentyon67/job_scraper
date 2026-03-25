# Job Scraper

Greenhouseの求人ページを収集・整形し、CSVとして出力するCLIツールです。
一覧ページ・詳細ページのHTML保存、失敗URLの再取得、CSV生成に加え、OpenAI APIを用いた求人要約機能を実装しています。

---

## Features

* 求人一覧ページのHTML取得
* 求人詳細ページのHTML取得
* 失敗URLの再取得
* 保存済みHTMLからCSV生成
* OpenAI APIを用いた求人要約
* CLIベースで各処理を実行可能

---

## Project Structure

job_scraper/
├── src/
│   ├── ai/
│   │   ├── summarize.py
│   │   └── test_ai.py
│   ├── build_dataset.py
│   ├── cli.py
│   ├── fetch_detail.py
│   ├── fetch_list.py
│   ├── parse_detail.py
│   ├── parse_list.py
│   ├── retry_failed.py
│   └── utils.py
├── data/
│   ├── raw/
│   └── output/
├── requirements.txt
└── README.md

---

## Setup

### 1. 仮想環境作成

python -m venv .venv
.venv\Scripts\activate

---

### 2. 依存関係インストール

python -m pip install -r requirements.txt

---

### 3. OpenAI APIキー設定

PowerShell:

setx OPENAI_API_KEY "your_api_key"

設定後、ターミナルを再起動してください。

---

## Usage

### 一覧ページ取得

python -m src.cli fetch-list

---

### 詳細ページ取得

python -m src.cli fetch-detail --max-jobs 20

---

### 失敗URL再取得

python -m src.cli retry --limit 5

---

### CSV生成

python -m src.cli build

---

### AI要約生成

python -m src.cli summarize --limit 5

---

## Output Files

* data/raw/list.html
* data/raw/detail_*.html
* data/output/jobs.csv
* data/output/jobs_enriched.csv

---

## AI Summarization

summarizeコマンドはjobs.csvを読み込み、OpenAI APIにより求人内容を要約し、
ai_summary列を追加したCSVを出力します。

---

## Example Output

| title            | location | ai_summary                                |
| ---------------- | -------- | ----------------------------------------- |
| Backend Engineer | Tokyo    | Pythonを用いたバックエンド開発が中心で、AWSやSQL経験が求められる求人。 |

---

## Tech Stack

* Python
* requests
* BeautifulSoup
* argparse
* pathlib
* OpenAI API

---

## Future Improvements

* AIによる求人分類
* スコアリング機能
* 求人比較機能
* スキル抽出
