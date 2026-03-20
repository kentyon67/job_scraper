from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = DATA_DIR / "logs"

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 20


def build_session() -> requests.Session:
    """共通ヘッダーを持つ Session を作成する。"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def extract_job_id(url: str) -> str:
    """URL末尾から job_id を取り出す。"""
    return url.rstrip("/").split("/")[-1]


def save_detail(url: str, html: str) -> None:
    """詳細HTMLと元URLを job_id ベースの名前で保存する。"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    job_id = extract_job_id(url)

    html_path = RAW_DIR / f"detail_{job_id}.html"
    url_path = RAW_DIR / f"detail_{job_id}.url.txt"

    html_path.write_text(html, encoding="utf-8")
    url_path.write_text(url, encoding="utf-8")