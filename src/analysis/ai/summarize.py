import csv
import logging
from pathlib import Path

from openai import OpenAI


DEFAULT_INPUT_PATH = Path("data/output/jobs.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_enriched.csv")

logger = logging.getLogger(__name__)


def build_prompt(row: dict) -> str:
    title = row.get("title", "")
    location = row.get("location", "")
    description = row.get("description", "")
    qualifications = row.get("qualifications", "")
    working_condition = row.get("working_condition", "")

    return f"""
以下の求人情報を日本語で3文以内で要約してください。
簡潔に、応募判断に役立つようにまとめてください。

【職種名】
{title}

【勤務地】
{location}

【仕事内容】
{description}

【応募要件】
{qualifications}

【勤務条件】
{working_condition}
""".strip()


def summarize_text(client: OpenAI, prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "あなたは求人情報を簡潔に要約するアシスタントです。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def summarize_jobs(
    input_path: Path,
    output_path: Path,
    limit: int | None = None,
) -> None:
    logger.info("Start summarizing jobs")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)
    logger.info("Limit: %s", limit)

    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return

    client = OpenAI()

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d rows from CSV", len(rows))

    if limit is not None:
        rows = rows[:limit]
        logger.info("Trimmed rows to %d by limit", len(rows))

    enriched_rows = []

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Processing row %d/%d: %s", i, len(rows), title)

        try:
            prompt = build_prompt(row)
            summary = summarize_text(client, prompt)

            new_row = dict(row)
            new_row["ai_summary"] = summary
            enriched_rows.append(new_row)

            logger.info("Completed row %d/%d", i, len(rows))

        except Exception as e:
            logger.exception("Failed to summarize row %d/%d: %s", i, len(rows), e)

    if not enriched_rows:
        logger.warning("No enriched rows were created. Skip writing output.")
        return

    fieldnames = list(enriched_rows[0].keys())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    logger.info("Wrote %d rows to %s", len(enriched_rows), output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    limit: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    summarize_jobs(
        input_path=input_path,
        output_path=output_path,
        limit=limit,
    )


if __name__ == "__main__":
    main()