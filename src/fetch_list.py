import logging
import time
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

LIST_MAX_ATTEMPTS = 2
LIST_RETRY_WAIT_SECONDS = 1

logger = logging.getLogger(__name__)


def sanitize_filename(text: str) -> str:
    sanitized = text.replace("https://", "").replace("http://", "")
    sanitized = sanitized.replace("/", "_").replace(":", "_").replace("?", "_")
    sanitized = sanitized.replace("&", "_").replace("=", "_")
    return sanitized


def fetch_html(url: str) -> str:
    for attempt in range(1, LIST_MAX_ATTEMPTS + 1):
        logger.info(
            "Fetching list page (attempt %d/%d): %s",
            attempt,
            LIST_MAX_ATTEMPTS,
            url,
        )

        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()

            html = resp.text
            logger.info("Fetched HTML: %s chars", len(html))
            return html

        except requests.RequestException as e:
            is_last_attempt = attempt == LIST_MAX_ATTEMPTS

            if is_last_attempt:
                logger.exception(
                    "Failed to fetch list page after %d attempts: %s",
                    LIST_MAX_ATTEMPTS,
                    url,
                )
                raise

            logger.warning(
                "Fetch list failed on attempt %d/%d. Retrying in %d second(s): %s",
                attempt,
                LIST_MAX_ATTEMPTS,
                LIST_RETRY_WAIT_SECONDS,
                url,
            )
            time.sleep(LIST_RETRY_WAIT_SECONDS)

    raise RuntimeError(f"Unexpected list fetch failure: {url}")

def save_list_html(html: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    logger.info("Saved list HTML: %s", out_path)


def fetch_and_save_list(
    url: str = DEFAULT_URL,
    out_path: Path = DEFAULT_OUT_PATH,
) -> Path:
    html = fetch_html(url)
    save_list_html(html, out_path)
    return out_path


def build_list_out_path(url: str, out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    filename = sanitize_filename(url)
    return out_dir / f"list_{filename}.html"


def fetch_and_save_multiple(
    urls: list[str],
    out_dir: Path = DEFAULT_OUT_DIR,
) -> list[Path]:
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
    url: str | None = DEFAULT_URL,
    urls: list[str] | None = None,
    out_path: Path | None = None,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> list[Path]:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    if urls:
        return fetch_and_save_multiple(urls=urls, out_dir=out_dir)

    target_url = url or DEFAULT_URL
    target_out_path = out_path or DEFAULT_OUT_PATH
    saved_path = fetch_and_save_list(url=target_url, out_path=target_out_path)
    return [saved_path]


if __name__ == "__main__":
    main()