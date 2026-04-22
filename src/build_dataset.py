from pathlib import Path
from urllib.parse import urlparse
import csv
import logging
import re

from bs4 import BeautifulSoup, Tag

from src.utils import RAW_DIR, OUTPUT_DIR


DEFAULT_DETAIL_DIR = RAW_DIR
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "jobs.csv"

logger = logging.getLogger(__name__)


def text_or_empty(tag: Tag | None) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def extract_sections(soup: BeautifulSoup) -> dict[str, str]:
    sections: dict[str, str] = {}
    container = soup.body or soup

    headings = container.find_all(["h2", "h3"])
    for h in headings:
        key = h.get_text(" ", strip=True)
        if not key:
            continue

        parts: list[str] = []
        cur = h.next_sibling

        while cur:
            if hasattr(cur, "name") and cur.name in ["h2", "h3"]:
                break

            if hasattr(cur, "name") and cur.name in ["p", "ul", "ol"]:
                txt = cur.get_text(" ", strip=True)
                if txt:
                    parts.append(txt)

            cur = cur.next_sibling

        if parts:
            sections[key] = "\n".join(parts)

    return sections


def extract_job_id_from_filename(html_path: Path) -> str:
    """
    detail_123456.html -> 123456
    """
    match = re.match(r"detail_(.+)\.html$", html_path.name)
    if not match:
        return html_path.stem
    return match.group(1)


def normalize_company_name(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def extract_company_name_from_url(url: str) -> str:
    """
    URLから会社名候補をできるだけ汎用的に推定する。

    優先順:
    1. pathに /<company>/jobs/ があれば <company>
    2. サブドメインの先頭
    3. ドメイン本体の先頭

    例:
    - https://job-boards.greenhouse.io/paypay/jobs/123
      -> paypay
    - https://careers.example.com/jobs/abc
      -> careers (弱いがフォールバック)
    - https://example.com/careers/jobs/abc
      -> example
    """
    if not url:
        return ""

    parsed = urlparse(url)
    hostname = parsed.netloc.lower().replace("www.", "")
    path_parts = [part for part in parsed.path.split("/") if part]

    # 1) /<company>/jobs/... 型
    for i, part in enumerate(path_parts[:-1]):
        if path_parts[i + 1] == "jobs":
            candidate = normalize_company_name(part)
            if candidate:
                return candidate

    # 2) サブドメイン先頭
    host_parts = hostname.split(".")
    if len(host_parts) >= 3:
        subdomain = normalize_company_name(host_parts[0])
        if subdomain and subdomain not in {"jobs", "careers", "app", "boards"}:
            return subdomain

    # 3) ドメイン本体
    if len(host_parts) >= 2:
        domain_root = normalize_company_name(host_parts[-2])
        if domain_root:
            return domain_root

    return ""


def extract_company_name(url: str, soup: BeautifulSoup | None = None) -> str:
    """
    将来拡張しやすい入口。
    現時点ではURLベース推定を使う。
    """
    return extract_company_name_from_url(url)


def build_job_key(company_name: str, job_id: str) -> str:
    company_part = company_name or "unknown-company"
    job_part = job_id or "unknown-job"
    return f"{company_part}__{job_part}"


def parse_file(html_path: Path) -> dict[str, str]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    title = text_or_empty(soup.find("h1"))
    location = text_or_empty(soup.select_one(".job__location"))
    sections = extract_sections(soup)

    url_path = html_path.with_suffix(".url.txt")
    url = url_path.read_text(encoding="utf-8").strip() if url_path.exists() else ""

    job_id = extract_job_id_from_filename(html_path)
    company_name = extract_company_name(url, soup=soup)
    job_key = build_job_key(company_name, job_id)

    return {
        "job_id": job_id,
        "job_key": job_key,
        "company_name": company_name,
        "url": url,
        "title": title,
        "location": location,
        "description": sections.get("Job Description", ""),
        "qualifications": sections.get("Qualifications", ""),
        "working_condition": sections.get("Working Condition", ""),
    }


def collect_rows(detail_dir: Path = DEFAULT_DETAIL_DIR) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for html_path in sorted(detail_dir.glob("detail_*.html")):
        rows.append(parse_file(html_path))

    logger.info("Collected %d rows from detail HTML files", len(rows))
    return rows


def save_csv(rows: list[dict[str, str]], output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "job_id",
                "job_key",
                "company_name",
                "url",
                "title",
                "location",
                "description",
                "qualifications",
                "working_condition",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.info("CSV saved to %s rows=%d", output_path, len(rows))


def main(
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> None:
    logger.info("Start building dataset")
    logger.info("Detail dir: %s", detail_dir)
    logger.info("Output path: %s", output_path)

    rows = collect_rows(detail_dir=detail_dir)

    if not rows:
        raise ValueError(f"No detail HTML files found in: {detail_dir}")

    save_csv(rows, output_path=output_path)

    logger.info("Build dataset completed")


if __name__ == "__main__":
    main()