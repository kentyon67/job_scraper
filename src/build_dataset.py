# src/build_dataset.py
from pathlib import Path
import csv

from bs4 import BeautifulSoup, Tag

DETAIL_DIR = Path("data/raw")
OUTPUT_PATH = Path("data/output/jobs.csv")


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


def parse_file(html_path: Path) -> dict[str, str]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    title = text_or_empty(soup.find("h1"))
    location = text_or_empty(soup.select_one(".job__location"))
    sections = extract_sections(soup)

    url_path = html_path.with_suffix(".url.txt")
    url = url_path.read_text(encoding="utf-8").strip() if url_path.exists() else ""

    return {
        "url": url,
        "title": title,
        "location": location,
        "description": sections.get("Job Description", ""),
        "qualifications": sections.get("Qualifications", ""),
        "working_condition": sections.get("Working Condition", ""),
    }


def main() -> None:
    rows: list[dict[str, str]] = []

    for html_path in sorted(DETAIL_DIR.glob("detail_*.html")):
        row = parse_file(html_path)
        rows.append(row)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
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

    print(f"[OK] CSV saved: {OUTPUT_PATH} rows={len(rows)}")


if __name__ == "__main__":
    main()