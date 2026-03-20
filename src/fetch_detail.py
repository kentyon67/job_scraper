from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
import csv
import logging

import requests
from bs4 import BeautifulSoup

from src.utils import (
    BASE_DIR,
    LOG_DIR,
    build_session,
    extract_job_id,
    save_detail,
    TIMEOUT,
)

LIST_PATH = BASE_DIR / "data" / "raw" / "list.html"
FAIL_LOG = LOG_DIR / "failures.csv"
BASE_URL = "https://job-boards.greenhouse.io"
DEFAULT_MAX_JOBS = 50

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_list_html(path: Path) -> str:
    logger.info("Loading list HTML from %s", path)
    return path.read_text(encoding="utf-8")


def extract_job_urls(list_html: str) -> list[str]:
    soup = BeautifulSoup(list_html, "lxml")

    job_urls: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/" in href:
            job_urls.append(urljoin(BASE_URL, href))

    unique_urls = list(dict.fromkeys(job_urls))
    logger.info("Extracted %d unique job URLs", len(unique_urls))
    return unique_urls


def log_failure(
    index: int,
    job_id: str,
    url: str,
    error: Exception,
    status_code: int | None,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = FAIL_LOG.exists()

    with FAIL_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "index",
                "job_id",
                "url",
                "status_code",
                "error_type",
                "message",
            ],
        )
        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "index": index,
                "job_id": job_id,
                "url": url,
                "status_code": status_code if status_code is not None else "",
                "error_type": type(error).__name__,
                "message": str(error),
            }
        )


def fetch_and_save_detail(session: requests.Session, index: int, url: str) -> None:
    job_id = extract_job_id(url)
    logger.info("[%d] job_id=%s fetching: %s", index, job_id, url)

    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()

        save_detail(url, resp.text)
        logger.info("[%d] job_id=%s saved successfully", index, job_id)

    except requests.exceptions.RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        logger.error("[%d] Request failed for %s: %s", index, url, e)
        log_failure(index, job_id, url, e, status)

    except OSError as e:
        logger.error("[%d] File save failed for %s: %s", index, url, e)
        log_failure(index, job_id, url, e, None)


def main(max_jobs: int = DEFAULT_MAX_JOBS) -> None:
    session = build_session()
    list_html = load_list_html(LIST_PATH)
    job_urls = extract_job_urls(list_html)

    logger.info("Processing up to %d jobs", max_jobs)

    for i, url in enumerate(job_urls[:max_jobs]):
        fetch_and_save_detail(session, i, url)

    logger.info("Done")


if __name__ == "__main__":
    main()