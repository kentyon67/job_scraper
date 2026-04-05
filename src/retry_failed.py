from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import logging

import requests

from src.utils import (
    LOG_DIR,
    build_session,
    extract_job_id,
    save_detail,
    TIMEOUT,
)

FAIL_LOG = LOG_DIR / "failures.csv"
RETRY_FAIL_LOG = LOG_DIR / "retry_failures.csv"

logger = logging.getLogger(__name__)


@dataclass
class RetryResult:
    target_count: int
    success_count: int
    failed_count: int
    retried_urls: list[str]
    failed_urls: list[str]


def load_failed_rows(fail_log_path: Path = FAIL_LOG) -> list[dict[str, str]]:
    if not fail_log_path.exists():
        logger.info("Failure log not found: %s", fail_log_path)
        return []

    with fail_log_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d failed rows from %s", len(rows), fail_log_path)
    return rows


def clear_retry_fail_log(retry_fail_log_path: Path = RETRY_FAIL_LOG) -> None:
    if retry_fail_log_path.exists():
        retry_fail_log_path.unlink()
        logger.info("Cleared old retry failure log: %s", retry_fail_log_path)


def log_retry_failure(
    index: int,
    job_id: str,
    url: str,
    error: Exception,
    status_code: int | None,
    retry_fail_log_path: Path = RETRY_FAIL_LOG,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = retry_fail_log_path.exists()

    with retry_fail_log_path.open("a", newline="", encoding="utf-8") as f:
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


def retry_single_row(
    session: requests.Session,
    row: dict[str, str],
    retry_fail_log_path: Path = RETRY_FAIL_LOG,
) -> bool:
    index = int(row["index"])
    url = row["url"]
    job_id = row.get("job_id") or extract_job_id(url)

    logger.info("[retry %d] job_id=%s fetching: %s", index, job_id, url)

    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()

        save_detail(url, resp.text)
        logger.info("[retry %d] job_id=%s retry success", index, job_id)
        return True

    except requests.exceptions.RequestException as e:
        status_code = getattr(getattr(e, "response", None), "status_code", None)
        logger.error("[retry %d] Request failed for %s: %s", index, url, e)
        log_retry_failure(
            index=index,
            job_id=job_id,
            url=url,
            error=e,
            status_code=status_code,
            retry_fail_log_path=retry_fail_log_path,
        )
        return False

    except OSError as e:
        logger.error("[retry %d] File save failed for %s: %s", index, url, e)
        log_retry_failure(
            index=index,
            job_id=job_id,
            url=url,
            error=e,
            status_code=None,
            retry_fail_log_path=retry_fail_log_path,
        )
        return False


def retry_failed_rows(
    limit: int | None = None,
    fail_log_path: Path = FAIL_LOG,
    retry_fail_log_path: Path = RETRY_FAIL_LOG,
) -> RetryResult:
    rows = load_failed_rows(fail_log_path=fail_log_path)

    if limit is not None:
        rows = rows[:limit]

    if not rows:
        logger.info("No failed rows to retry")
        return RetryResult(
            target_count=0,
            success_count=0,
            failed_count=0,
            retried_urls=[],
            failed_urls=[],
        )

    clear_retry_fail_log(retry_fail_log_path)

    session = build_session()

    success_count = 0
    failed_count = 0
    retried_urls: list[str] = []
    failed_urls: list[str] = []

    logger.info("Retry target count: %d", len(rows))

    for row in rows:
        url = row["url"]
        retried_urls.append(url)

        is_success = retry_single_row(
            session=session,
            row=row,
            retry_fail_log_path=retry_fail_log_path,
        )

        if is_success:
            success_count += 1
        else:
            failed_count += 1
            failed_urls.append(url)

    result = RetryResult(
        target_count=len(rows),
        success_count=success_count,
        failed_count=failed_count,
        retried_urls=retried_urls,
        failed_urls=failed_urls,
    )

    logger.info(
        "Retry completed: target=%d success=%d failed=%d",
        result.target_count,
        result.success_count,
        result.failed_count,
    )
    return result


def main(limit: int | None = None) -> RetryResult:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return retry_failed_rows(limit=limit)


if __name__ == "__main__":
    main()