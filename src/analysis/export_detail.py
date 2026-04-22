import csv
import logging
from pathlib import Path

DEFAULT_INPUT_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_detail_view.csv")

logger = logging.getLogger(__name__)

DETAIL_COLUMNS = [
    "job_id",
    "job_key",
    "company_name",
    "title",
    "title_ja",
    "url",
    "location",
    "job_category",
    "language_tags",
    "work_style",
    "employment_type",
    "experience_level_hint",
    "global_related",
    "tech_keywords",
    "ai_related",
    "ai_summary",
    "description",
    "description_ja",
    "qualifications",
    "qualifications_ja",
    "working_condition",
    "working_condition_ja",
]


def export_detail_view(
    input_path: Path,
    output_path: Path,
) -> None:
    logger.info("Start exporting detail base view")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d rows from CSV", len(rows))

    if not rows:
        raise ValueError("No rows found in input CSV")

    detail_rows: list[dict[str, str]] = []

    for row in rows:
        detail_row = {
            "job_id": row.get("job_id", ""),
            "job_key": row.get("job_key", ""),
            "company_name": row.get("company_name", ""),
            "title": row.get("title", ""),
            "title_ja": row.get("title_ja", ""),
            "url": row.get("url", ""),
            "location": row.get("location", ""),
            "job_category": row.get("job_category", ""),
            "language_tags": row.get("language_tags", ""),
            "work_style": row.get("work_style", ""),
            "employment_type": row.get("employment_type", ""),
            "experience_level_hint": row.get("experience_level_hint", ""),
            "global_related": row.get("global_related", ""),
            "tech_keywords": row.get("tech_keywords", ""),
            "ai_related": row.get("ai_related", ""),
            "ai_summary": row.get("ai_summary", ""),
            "description": row.get("description", ""),
            "description_ja": row.get("description_ja", ""),
            "qualifications": row.get("qualifications", ""),
            "qualifications_ja": row.get("qualifications_ja", ""),
            "working_condition": row.get("working_condition", ""),
            "working_condition_ja": row.get("working_condition_ja", ""),
        }
        detail_rows.append(detail_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DETAIL_COLUMNS)
        writer.writeheader()
        writer.writerows(detail_rows)

    logger.info("Saved detail base CSV: %s", output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    export_detail_view(
        input_path=input_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()