from pathlib import Path

DETAIL_DIR = Path("data/raw")


def extract_job_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def save_detail(url: str, html: str) -> None:
    DETAIL_DIR.mkdir(parents=True, exist_ok=True)

    job_id = extract_job_id(url)

    html_path = DETAIL_DIR / f"detail_{job_id}.html"
    url_path = DETAIL_DIR / f"detail_{job_id}.url.txt"

    html_path.write_text(html, encoding="utf-8")
    url_path.write_text(url, encoding="utf-8")