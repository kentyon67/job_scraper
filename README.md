# Job Scraper (Python CLI)

求人情報をスクレイピングし、
一覧取得 → 詳細取得 → 失敗再試行 → CSV化までを行う
CLIベースのPythonツールです。

---

## 📌 Features

* 求人一覧ページの取得
* 各求人詳細ページの取得
* `job_id` ベースでのファイル管理
* 失敗URLのCSVログ保存
* 失敗データの再取得（retry機能）
* HTMLからCSVデータセット生成
* `argparse` によるCLI操作
* `requests.Session` による通信効率化

---

## 📂 Project Structure

```
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
│  ├─ processed/
│  └─ logs/
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## ⚙️ Setup

```bash
git clone <YOUR_REPOSITORY_URL>
cd job_scraper

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## 🚀 Usage

### ① 一覧ページ取得

```bash
python -m src.cli fetch-list
```

---

### ② 詳細ページ取得

```bash
python -m src.cli fetch-detail --max-jobs 20
```

---

### ③ 失敗データ再取得

```bash
python -m src.cli retry --limit 10
```

---

### ④ CSVデータ生成

```bash
python -m src.cli build
```

---

## 📊 Output

* 一覧HTML（data/raw）
* 詳細HTML（data/raw）
* 失敗ログCSV（data/logs）
* 整形済みCSV（data/processed）

---

## 🛠 Tech Stack

* Python
* requests
* BeautifulSoup
* argparse
* csv
* pathlib

---

## 💡 Design Points

* `requests.Session` により通信効率を改善
* `job_id` ベースでファイルを一意管理
* 失敗ログ＋retry機能により耐障害性を向上
* CLIサブコマンド設計により機能を分離

---

## 🔧 Future Improvements

* logging導入
* テストコード追加
* 設定ファイル化（config分離）
* 並列処理対応
* rate limit対策

---

## ⚠️ Notes

対象サイトの利用規約・robots.txtを確認した上で使用してください。
