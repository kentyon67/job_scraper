import csv
import json
import logging
from pathlib import Path

from openai import OpenAI


DEFAULT_INPUT_PATH = Path("data/output/jobs_enriched.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_translated.csv")
DEFAULT_MODEL = "gpt-4o-mini"

logger = logging.getLogger(__name__)


def build_client() -> OpenAI:
    return OpenAI()


def build_prompt(row: dict) -> str:
    title = row.get("title", "")
    description = row.get("description", "")
    qualifications = row.get("qualifications", "")
    working_condition = row.get("working_condition", "")

    return f"""
あなたは求人表示向けの翻訳アシスタントです。
以下の英語求人情報を、一般の日本語ユーザーにも分かりやすい自然な日本語へ変換してください。

ルール:
- 技術用語は必要に応じて英語を残してよい
- 不自然な直訳は避ける
- タイトルは短く、職種名として自然な日本語にする
- 内容を勝手に追加しない
- JSONのみを返す

返すJSONの形式:
{{
  "title_ja": "...",
  "description_ja": "...",
  "qualifications_ja": "...",
  "working_condition_ja": "..."
}}

title:
{title}

description:
{description}

qualifications:
{qualifications}

working_condition:
{working_condition}
""".strip()


def translate_row(client: OpenAI, row: dict, model: str = DEFAULT_MODEL) -> dict[str, str]:
    prompt = build_prompt(row)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a precise translation assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    data = json.loads(content)

    return {
        "title_ja": data.get("title_ja", ""),
        "description_ja": data.get("description_ja", ""),
        "qualifications_ja": data.get("qualifications_ja", ""),
        "working_condition_ja": data.get("working_condition_ja", ""),
    }


def translate_fields(
    input_path: Path,
    output_path: Path,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> None:
    logger.info("Start translating display fields")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)
    logger.info("Limit: %s", limit)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if limit is not None:
        rows = rows[:limit]

    if not rows:
        raise ValueError("No rows found in input CSV")

    client = build_client()
    translated_rows = []

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Translating row %d/%d: %s", i, len(rows), title)

        try:
            ja_fields = translate_row(client, row, model=model)
            new_row = dict(row)
            new_row.update(ja_fields)
            translated_rows.append(new_row)

        except Exception as e:
            logger.exception("Failed to translate row %d/%d: %s", i, len(rows), e)
            new_row = dict(row)
            new_row["title_ja"] = row.get("title", "")
            new_row["description_ja"] = row.get("description", "")
            new_row["qualifications_ja"] = row.get("qualifications", "")
            new_row["working_condition_ja"] = row.get("working_condition", "")
            translated_rows.append(new_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(translated_rows[0].keys())

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(translated_rows)

    logger.info("Wrote translated rows to %s", output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    translate_fields(
        input_path=input_path,
        output_path=output_path,
        limit=limit,
        model=model,
    )


if __name__ == "__main__":
    main()