from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
import csv
import logging
import time
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

DEFAULT_LIST_PATH = BASE_DIR / "data" / "raw" / "list.html"
FAIL_LOG = LOG_DIR / "failures.csv"
DEFAULT_BASE_URL = "https://job-boards.greenhouse.io"
DEFAULT_MAX_JOBS = 50
DETAIL_RETRY_WAIT_SECONDS = 1
DETAIL_MAX_ATTEMPTS = 2
logger = logging.getLogger(__name__)



def load_list_html(path: Path) -> str:
    logger.info("Loading list HTML from %s", path)
    return path.read_text(encoding="utf-8")


def extract_job_urls(list_html: str, base_url: str = DEFAULT_BASE_URL) -> list[str]:
    soup = BeautifulSoup(list_html, "lxml")

    job_urls: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/" in href:
            job_urls.append(urljoin(base_url, href))

    unique_urls = list(dict.fromkeys(job_urls))
    logger.info("Extracted %d unique job URLs", len(unique_urls))
    return unique_urls


def extract_job_urls_from_file(
    list_path: Path,
    base_url: str = DEFAULT_BASE_URL,
) -> list[str]:
    list_html = load_list_html(list_path)
    return extract_job_urls(list_html, base_url=base_url)


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


def fetch_and_save_detail(
    session: requests.Session,
    index: int,
    url: str,
) -> bool:
    job_id = extract_job_id(url)

    for attempt in range(1, DETAIL_MAX_ATTEMPTS + 1):
        logger.info(
            "[%d] job_id=%s fetching (attempt %d/%d): %s",
            index,
            job_id,
            attempt,
            DETAIL_MAX_ATTEMPTS,
            url,
        )

        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()

            save_detail(url, resp.text)
            logger.info("[%d] job_id=%s saved successfully", index, job_id)
            return True

        except requests.exceptions.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)

            is_last_attempt = attempt == DETAIL_MAX_ATTEMPTS
            if is_last_attempt:
                logger.error("[%d] Request failed for %s: %s", index, url, e)
                log_failure(index, job_id, url, e, status)
                return False

            logger.warning(
                "[%d] Request failed for %s on attempt %d/%d. Retrying...",
                index,
                url,
                attempt,
                DETAIL_MAX_ATTEMPTS,
            )
            time.sleep(DETAIL_RETRY_WAIT_SECONDS)

        except OSError as e:
            logger.error("[%d] File save failed for %s: %s", index, url, e)
            log_failure(index, job_id, url, e, None)
            return False

def fetch_details_from_urls(
    urls: list[str],
    max_jobs: int = DEFAULT_MAX_JOBS,
    session: requests.Session | None = None,
) -> list[str]:
    """
    URLリストから求人詳細を取得・保存する。
    保存対象として処理したURL一覧を返す。
    """
    if session is None:
        session = build_session()

    target_urls = urls[:max_jobs]
    logger.info("Processing %d detail URLs", len(target_urls))

    success_count = 0
    failed_count = 0

    for i, url in enumerate(target_urls, start=1):
        ok =fetch_and_save_detail(session, i, url)

    if ok :
        success_count = success_count + 1
    else:
        failed_count = failed_count + 1

    logger.info(
        "Detail fetch completed: target=%d success=%d failed=%d",
        len(target_urls),
        success_count,
        failed_count,
    )
    return target_urls


def fetch_details_from_list_path(
    list_path: Path = DEFAULT_LIST_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
    base_url: str = DEFAULT_BASE_URL,
    session: requests.Session | None = None,
) -> list[str]:
    """
    1つの一覧HTMLファイルから求人URLを抽出し、詳細取得を行う。
    """
    job_urls = extract_job_urls_from_file(list_path, base_url=base_url)
    return fetch_details_from_urls(job_urls, max_jobs=max_jobs, session=session)


def fetch_details_from_multiple_list_paths(
    list_paths: list[Path],
    max_jobs_per_list: int = DEFAULT_MAX_JOBS,
    base_url: str = DEFAULT_BASE_URL,
) -> list[str]:
    """
    複数の一覧HTMLファイルを順番に処理する。
    成功可否にかかわらず、対象として処理したURL一覧を返す。
    """
    session = build_session()
    processed_urls: list[str] = []

    for i, list_path in enumerate(list_paths, start=1):
        logger.info("Processing list file %d/%d: %s", i, len(list_paths), list_path)

        try:
            job_urls = extract_job_urls_from_file(list_path, base_url=base_url)
            target_urls = fetch_details_from_urls(
                job_urls,
                max_jobs=max_jobs_per_list,
                session=session,
            )
            processed_urls.extend(target_urls)

        except OSError as e:
            logger.exception("Failed to process list file %s: %s", list_path, e)

    return processed_urls


def main(
    list_path: Path | None = DEFAULT_LIST_PATH,
    list_paths: list[Path] | None = None,
    max_jobs: int = DEFAULT_MAX_JOBS,
    base_url: str = DEFAULT_BASE_URL,
) -> list[str]:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if list_paths:
        return fetch_details_from_multiple_list_paths(
            list_paths=list_paths,
            max_jobs_per_list=max_jobs,
            base_url=base_url,
        )

    target_list_path = list_path or DEFAULT_LIST_PATH
    return fetch_details_from_list_path(
        list_path=target_list_path,
        max_jobs=max_jobs,
        base_url=base_url,
    )


if __name__ == "__main__":
    main()