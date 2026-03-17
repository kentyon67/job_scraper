from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
import csv

import requests
from bs4 import BeautifulSoup

from src.utils import extract_job_id, save_detail


LIST_PATH = Path("data/raw/list.html")
DETAIL_DIR = Path("data/raw")
LOG_DIR = Path("data/logs")
FAIL_LOG = LOG_DIR / "failures.csv"

BASE_URL = "https://job-boards.greenhouse.io"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DEFAULT_MAX_JOBS = 50




def log_failure(i: int, job_id: str,url: str, e: Exception, status_code: int | None) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = FAIL_LOG.exists()

    with open(FAIL_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "index","job_id", "url", "status_code", "error_type", "message"],
        )
        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "index": i,
                "job_id": job_id,
                "url": url,
                "status_code": status_code if status_code is not None else "",
                "error_type": type(e).__name__,
                "message": str(e),
            }
        )


def main(max_jobs:int =DEFAULT_MAX_JOBS) -> None:
    session = requests.Session()
    session.headers.update(HEADERS)

    html = LIST_PATH.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    job_urls: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/" in href:
            job_urls.append(urljoin(BASE_URL, href))

    job_urls = list(dict.fromkeys(job_urls))

    print("求人URL件数:", len(job_urls))

    DETAIL_DIR.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(job_urls[:max_jobs]):

        job_id = extract_job_id(url)
        print(f"[{i}],job_id=[{job_id}] fetching:", url)

        try:
            resp= session.get(url, timeout=20)
            resp.raise_for_status()

            save_detail(url, resp.text)

        except requests.exceptions.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            print("ERROR(Request):", url, e)
            log_failure(i,job_id, url, e, status)
            continue
        except OSError as e:
            print("ERROR(File):", url, e)
            log_failure(i, job_id,url, e, None)
            continue

    print("[OK] done")


if __name__ == "__main__":
    main()