import logging
from pathlib import Path

import requests


DEFAULT_URL = "https://job-boards.greenhouse.io/paypay"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

TIMEOUT = 20

DEFAULT_OUT_PATH = Path("data/raw/list.html")
DEFAULT_OUT_DIR = Path("data/raw")

logger = logging.getLogger(__name__)


def sanitize_filename(text: str) -> str:
    """
    URLなどからファイル名に使いやすい文字列を作る。
    """
    sanitized = text.replace("https://", "").replace("http://", "")
    sanitized = sanitized.replace("/", "_").replace(":", "_").replace("?", "_")
    sanitized = sanitized.replace("&", "_").replace("=", "_")
    return sanitized


def fetch_html(url: str) -> str:
    """
    指定URLからHTMLを取得して返す。
    """
    logger.info("Fetching list page: %s", url)

    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()

    html = resp.text
    logger.info("Fetched HTML: %s chars", len(html))
    return html


def save_list_html(html: str, out_path: Path) -> None:
    """
    HTML文字列を指定パスに保存する。
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    logger.info("Saved list HTML: %s", out_path)


def fetch_and_save_list(
    url: str = DEFAULT_URL,
    out_path: Path = DEFAULT_OUT_PATH,
) -> Path:
    """
    1件のURLについて、一覧HTMLを取得して保存する。
    保存先Pathを返す。
    """
    html = fetch_html(url)
    save_list_html(html, out_path)
    return out_path


def build_list_out_path(url: str, out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    """
    複数URL対応用。
    URLごとに衝突しにくい一覧HTML保存パスを作る。
    """
    filename = sanitize_filename(url)
    return out_dir / f"list_{filename}.html"


def fetch_and_save_multiple(
    urls: list[str],
    out_dir: Path = DEFAULT_OUT_DIR,
) -> list[Path]:
    """
    複数URLの一覧HTMLを順番に取得・保存する。
    成功した保存先Pathのリストを返す。
    """
    saved_paths: list[Path] = []

    for i, url in enumerate(urls, start=1):
        logger.info("Processing list URL %d/%d: %s", i, len(urls), url)

        try:
            out_path = build_list_out_path(url, out_dir=out_dir)
            saved_path = fetch_and_save_list(url=url, out_path=out_path)
            saved_paths.append(saved_path)
        except requests.RequestException as e:
            logger.exception("Failed to fetch list URL %d/%d: %s", i, len(urls), e)

    return saved_paths


def main(
    url: str = DEFAULT_URL,
    out_path: Path = DEFAULT_OUT_PATH,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    saved_path = fetch_and_save_list(url=url, out_path=out_path)
    print(f"[OK] saved: {saved_path}")


if __name__ == "__main__":
    main()