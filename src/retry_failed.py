from pathlib import Path
from datetime import datetime
import csv

import requests

from src.utils import extract_job_id,save_detail
FAIL_LOG = Path("data/logs/failures.csv")
RETRY_FAIL_LOG = Path("data/logs/retry_failures.csv")
DETAIL_DIR = Path("data/raw")
LOG_DIR = Path("data/logs")

HEADERS = {"User-Agent": "Mozilla/5.0"}



def load_failed_rows() -> list[dict[str, str]]:
    if not FAIL_LOG.exists():
        print("failures.csv が見つかりません")
        return []

    with open(FAIL_LOG, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return rows


def log_retry_failure(index: int,job_id:str, url: str, e: Exception, status_code: int | None) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = RETRY_FAIL_LOG.exists()

    with open(RETRY_FAIL_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "job_id","index", "url", "status_code", "error_type", "message"],
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
                "error_type": type(e).__name__,
                "message": str(e),
            }
        )


def main(limit:int | None=None) -> None:

    session = requests.Session()
    session.headers.update(HEADERS)

    rows = load_failed_rows()


    if limit is not None:
        rows = rows[:limit]

    print("再取得対象件数:", len(rows))

    for row in rows:

        index = int(row["index"])
        url = row["url"]

        job_id = extract_job_id(url)
        print(f"[retry{index}]job_id={job_id}fetching:", url)

        try:
            resp =session.get(url,timeout=20)
            resp.raise_for_status()

            save_detail(url, resp.text)

            print(f"[OK] retry success: {job_id}")

        except requests.exceptions.RequestException as e:

            status = getattr(getattr(e, "response", None), "status_code", None)
            print("ERROR(Request Retry):", url, e)
            log_retry_failure(index,job_id, url, e, status)

        except OSError as e:

            print("ERROR(File Retry):", url, e)
            log_retry_failure(index, job_id,url, e, None)


        print("[OK] retry done")


if __name__ == "__main__":
    main()