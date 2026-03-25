import csv
import os
from pathlib import Path

from openai import OpenAI

DEFAULT_INPUT_PATH = Path("data/output/job.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/job_enriched.csv")

def build_prompt(row: dict) -> str:
    title = row.get("title","")
    location = row.get("location","")
    description = row.get("description","")
    qualifications = row.get("qualifications","")
    working_condition = row.get("working_condition","")

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

def summarize_text(client: OpenAI,prompt: str) -> str:
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
    client = OpenAI()

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if limit is not None:
        rows = rows[:limit]

    enriched_rows = []

    for row in rows:
        prompt = build_prompt(row)
        summary = summarize_text(client, prompt)

        new_row = dict(row)
        new_row["ai_summary"] = summary
        enriched_rows.append(new_row)

    if not enriched_rows:
        return

    fieldnames = list(enriched_rows[0].keys())

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)


def main(
    input_path : Path = DEFAULT_INPUT_PATH,
    output_path : Path =  DEFAULT_OUTPUT_PATH,
    limit : int | None = None,) -> None:
    summarize_jobs(
        input_path = input_path,
        output_path = output_path,
        limit = limit,
    )

if __name__ == "__main__":
    main()