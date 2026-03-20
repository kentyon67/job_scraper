# src/fetch_list.py
from pathlib import Path
import logging
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_PATH = BASE_DIR / "data" / "raw" / "list.html"

URL = "https://job-boards.greenhouse.io/paypay"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

TIMEOUT = 20  #seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def build_session() -> requests.Session:
    """共通ヘッダーを持つ Session を作成する。"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_list_html(session: requests.Session, url: str) -> str:
    """一覧ページのHTMLを取得して文字列で返す。"""
    logger.info("Fetching list page: %s", url)
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


def save_html(html: str, out_path: Path) -> None:
    """取得したHTMLをファイルに保存する。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    logger.info("Saved HTML to %s (chars=%d)", out_path, len(html))


def main() -> None:
    session = build_session()
    html = fetch_list_html(session, URL)
    save_html(html, OUT_PATH)


if __name__ == "__main__":
    main()