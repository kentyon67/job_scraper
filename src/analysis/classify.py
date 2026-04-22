import csv
import json
import logging
from pathlib import Path

from openai import OpenAI


DEFAULT_INPUT_PATH = Path("data/output/jobs_translated.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_MODEL = "gpt-4o-mini"

logger = logging.getLogger(__name__)


def build_classification_prompt(row: dict) -> str:
    title = row.get("title", "")
    title_ja = row.get("title_ja", "")
    location = row.get("location", "")
    description = row.get("description", "")
    description_ja = row.get("description_ja", "")
    qualifications = row.get("qualifications", "")
    qualifications_ja = row.get("qualifications_ja", "")
    working_condition = row.get("working_condition", "")
    working_condition_ja = row.get("working_condition_ja", "")
    ai_summary = row.get("ai_summary", "")

    return f"""
以下の求人情報を読んで、指定したJSON形式で分類結果を返してください。

【分類ルール】
- job_category は次のいずれか1つ:
  Backend, Frontend, Data, AI/ML, Mobile, Infra/SRE, Security, Product, Other

- language_tags は求人で求められている、または明確に関連する言語・主要技術を配列で返す
  例: ["Python", "SQL", "Go", "TypeScript", "Java", "Kotlin", "Scala", "JavaScript", "C++", "C#", "Rust", "PHP", "Ruby"]

- ai_related は "Yes" または "No"

- work_style は次のいずれか1つ:
  Remote, Hybrid, Onsite, Unknown

- employment_type は次のいずれか1つ:
  Internship, NewGrad, FullTime, Contract, PartTime, Unknown

- experience_level_hint は次のいずれか1つ:
  Beginner, Intermediate, Advanced, Unknown

- global_related は "Yes" または "No"

- tech_keywords は主要技術キーワードを配列で返す
  例: ["AWS", "Docker", "Kubernetes", "FastAPI", "Django", "Flask", "Airflow", "Spark", "React", "Node.js"]

【出力形式】
必ず以下のJSON形式のみを返してください。説明文は不要です。

{{
  "job_category": "...",
  "language_tags": ["..."],
  "ai_related": "...",
  "work_style": "...",
  "employment_type": "...",
  "experience_level_hint": "...",
  "global_related": "...",
  "tech_keywords": ["..."]
}}

【求人情報】
[title]
{title}

[title_ja]
{title_ja}

[location]
{location}

[description]
{description}

[description_ja]
{description_ja}

[qualifications]
{qualifications}

[qualifications_ja]
{qualifications_ja}

[working_condition]
{working_condition}

[working_condition_ja]
{working_condition_ja}

[ai_summary]
{ai_summary}
""".strip()


def classify_text(client: OpenAI, prompt: str, model: str = DEFAULT_MODEL) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a job classification assistant. "
                    "Return JSON only. "
                    "Do not add explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)


def normalize_string_list(values: list) -> str:
    """
    配列で返ってきた値を '|' 区切り文字列に変換する。
    CSVに入れやすくするため。
    """
    if not isinstance(values, list):
        return ""

    cleaned = []
    for value in values:
        text = str(value).strip()
        if text and text not in cleaned:
            cleaned.append(text)

    return "|".join(cleaned)


def classify_jobs(
    input_path: Path,
    output_path: Path,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> None:
    logger.info("Start classifying jobs")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)
    logger.info("Limit: %s", limit)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    client = OpenAI()

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d rows from CSV", len(rows))

    if limit is not None:
        rows = rows[:limit]
        logger.info("Trimmed rows to %d by limit", len(rows))

    if not rows:
        raise ValueError("No rows found in input CSV")

    classified_rows = []

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Processing row %d/%d: %s", i, len(rows), title)

        try:
            prompt = build_classification_prompt(row)
            result = classify_text(client, prompt, model=model)

            new_row = dict(row)
            new_row["job_category"] = result.get("job_category", "")
            new_row["language_tags"] = normalize_string_list(result.get("language_tags", []))
            new_row["ai_related"] = result.get("ai_related", "")
            new_row["work_style"] = result.get("work_style", "")
            new_row["employment_type"] = result.get("employment_type", "")
            new_row["experience_level_hint"] = result.get("experience_level_hint", "")
            new_row["global_related"] = result.get("global_related", "")
            new_row["tech_keywords"] = normalize_string_list(result.get("tech_keywords", []))

            classified_rows.append(new_row)
            logger.info("Completed row %d/%d", i, len(rows))

        except Exception as e:
            logger.exception("Failed to classify row %d/%d: %s", i, len(rows), e)

            # 失敗しても行を捨てない
            new_row = dict(row)
            new_row["job_category"] = "Other"
            new_row["language_tags"] = ""
            new_row["ai_related"] = "No"
            new_row["work_style"] = "Unknown"
            new_row["employment_type"] = "Unknown"
            new_row["experience_level_hint"] = "Unknown"
            new_row["global_related"] = "No"
            new_row["tech_keywords"] = ""
            classified_rows.append(new_row)

    if not classified_rows:
        raise ValueError("No classified rows were created")

    fieldnames = list(classified_rows[0].keys())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)

    logger.info("Classification completed: rows=%d", len(classified_rows))


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> None:
    classify_jobs(
        input_path=input_path,
        output_path=output_path,
        limit=limit,
        model=model,
    )


if __name__ == "__main__":
    main()