import csv
import json
import logging
from pathlib import Path

from openai import OpenAI


DEFAULT_INPUT_PATH = Path("data/output/jobs_enriched.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_classified.csv")

logger = logging.getLogger(__name__)


def build_classification_prompt(row: dict) -> str:
    title = row.get("title", "")
    location = row.get("location", "")
    description = row.get("description", "")
    qualifications = row.get("qualifications", "")
    working_condition = row.get("working_condition", "")
    ai_summary = row.get("ai_summary", "")

    return f"""
以下の求人情報を読んで、指定したJSON形式で分類結果を返してください。

【分類ルール】
- job_category は次のいずれか1つ:
  Backend, Frontend, Data, AI/ML, Mobile, Infra/SRE, Security, Product, Other
- python_related は Yes または No
- ai_related は Yes または No

【出力形式】
必ず以下のJSON形式のみを返してください。説明文は不要です。

{{
  "job_category": "...",
  "python_related": "...",
  "ai_related": "..."
}}

【求人情報】
[title]
{title}

[location]
{location}

[description]
{description}

[qualifications]
{qualifications}

[working_condition]
{working_condition}

[ai_summary]
{ai_summary}
""".strip()


def classify_text(client: OpenAI, prompt: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "あなたは求人情報を構造化分類するアシスタントです。必ずJSONのみを返してください。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)


def classify_jobs(
    input_path: Path,
    output_path: Path,
    limit: int | None = None,
) -> None:
    logger.info("Start classifying jobs")
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

    classified_rows = []

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Processing row %d/%d: %s", i, len(rows), title)

        try:
            prompt = build_classification_prompt(row)
            result = classify_text(client, prompt)

            new_row = dict(row)
            new_row["job_category"] = result.get("job_category", "")
            new_row["python_related"] = result.get("python_related", "")
            new_row["ai_related"] = result.get("ai_related", "")

            classified_rows.append(new_row)

            logger.info("Completed row %d/%d", i, len(rows))

        except Exception as e:
            logger.exception("Failed to classify row %d/%d: %s", i, len(rows), e)

    if not classified_rows:
        logger.warning("No classified rows were created. Skip writing output.")
        return

    fieldnames = list(classified_rows[0].keys())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)

    logger.info("Wrote %d rows to %s", len(classified_rows), output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    limit: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    classify_jobs(
        input_path=input_path,
        output_path=output_path,
        limit=limit,
    )


if __name__ == "__main__":
    main(limit=3)