import csv
import logging
from pathlib import Path

DEFAULT_INPUT_PATH = Path("data/output/jobs_scored.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_detail_view.csv")

VALID_SORT_COLUMNS = {"total_score", "job_score", "fit_score"}

logger = logging.getLogger(__name__)

DETAIL_COLUMNS = [
    "title",
    "url",
    "location",
    "job_category",
    "total_score",
    "fit_score",
    "job_score",
    "score_reason",
    "description",
    "qualifications",
    "working_condition",
    "ai_summary",
    "python_related",
    "ai_related",
]


def parse_score(value: str) -> int:
    if not value:
        return 0

    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid score value: %s", value)
        return 0


def validate_sort_by(sort_by: str) -> None:
    if sort_by not in VALID_SORT_COLUMNS:
        raise ValueError(
            f"sort_by must be one of {sorted(VALID_SORT_COLUMNS)}, got: {sort_by}"
        )


def export_detail_view(
    input_path: Path,
    output_path: Path,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logger.info("Start exporting detail view")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)
    logger.info("Sort by: %s", sort_by)
    logger.info("Top: %s", top)

    validate_sort_by(sort_by)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d rows from CSV", len(rows))

    if not rows:
        raise ValueError("No rows found in input CSV")

    sorted_rows = sorted(
        rows,
        key=lambda row: parse_score(row.get(sort_by, "0")),
        reverse=True,
    )

    if top is not None:
        sorted_rows = sorted_rows[:top]
        logger.info("Trimmed detail rows to top %d", len(sorted_rows))

    detail_rows: list[dict[str, str]] = []

    for row in sorted_rows:
        detail_row = {
            "title": row.get("title", ""),
            "url": row.get("url", ""),
            "location": row.get("location", ""),
            "job_category": row.get("job_category", ""),
            "total_score": row.get("total_score", ""),
            "fit_score": row.get("fit_score", ""),
            "job_score": row.get("job_score", ""),
            "score_reason": row.get("score_reason", ""),
            "description": row.get("description", ""),
            "qualifications": row.get("qualifications", ""),
            "working_condition": row.get("working_condition", ""),
            "ai_summary": row.get("ai_summary", ""),
            "python_related": row.get("python_related", ""),
            "ai_related": row.get("ai_related", ""),
        }
        detail_rows.append(detail_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DETAIL_COLUMNS)
        writer.writeheader()
        writer.writerows(detail_rows)

    logger.info("Saved detail view CSV: %s", output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    export_detail_view(
        input_path=input_path,
        output_path=output_path,
        sort_by=sort_by,
        top=top,
    )


if __name__ == "__main__":
    main()