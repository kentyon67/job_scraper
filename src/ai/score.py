import csv
import logging
from pathlib import Path


DEFAULT_INPUT_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_OUTPUT_PATH = Path("data/output/jobs_scored.csv")

logger = logging.getLogger(__name__)


GLOBAL_KEYWORDS = [
    "english",
    "global",
    "international",
    "overseas",
    "bilingual",
]

ENTRY_KEYWORDS = [
    "junior",
    "entry",
    "new grad",
    "internship",
    "trainee",
    "beginner",
]


def contains_any_keyword(text: str, keywords: list[str]) -> bool:
    lower_text = text.lower()
    return any(keyword in lower_text for keyword in keywords)


def calculate_job_score(row: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    python_related = row.get("python_related", "")
    ai_related = row.get("ai_related", "")
    job_category = row.get("job_category", "")
    ai_summary = row.get("ai_summary", "")
    qualifications = row.get("qualifications", "")
    description = row.get("description", "")

    combined_text = " ".join([ai_summary, qualifications, description])

    if python_related == "Yes":
        score += 35
        reasons.append("Python関連")

    if ai_related == "Yes":
        score += 25
        reasons.append("AI関連")

    category_scores = {
        "Backend": 20,
        "Data": 20,
        "AI/ML": 20,
        "Infra/SRE": 15,
        "Security": 10,
        "Frontend": 5,
        "Mobile": 5,
        "Product": 5,
        "Other": 0,
    }

    category_score = category_scores.get(job_category, 0)
    score += category_score
    if category_score > 0:
        reasons.append(f"{job_category}カテゴリ")

    if contains_any_keyword(combined_text, GLOBAL_KEYWORDS):
        score += 20
        reasons.append("英語・グローバル要素あり")

    return min(score, 100), reasons


def calculate_fit_score(row: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    python_related = row.get("python_related", "")
    ai_related = row.get("ai_related", "")
    job_category = row.get("job_category", "")
    ai_summary = row.get("ai_summary", "")
    qualifications = row.get("qualifications", "")
    description = row.get("description", "")

    combined_text = " ".join([ai_summary, qualifications, description])

    if python_related == "Yes":
        score += 30
        reasons.append("Python志向と一致")

    if ai_related == "Yes":
        score += 20
        reasons.append("AI志向と一致")

    if job_category in {"Backend", "Data", "AI/ML"}:
        score += 20
        reasons.append(f"{job_category}志向と一致")
    elif job_category == "Infra/SRE":
        score += 10
        reasons.append("技術志向と一定一致")

    if contains_any_keyword(combined_text, GLOBAL_KEYWORDS):
        score += 15
        reasons.append("外資・英語志向と一致")

    if contains_any_keyword(combined_text, ENTRY_KEYWORDS):
        score += 15
        reasons.append("学習・挑戦しやすい可能性")

    return min(score, 100), reasons


def build_score_reason(job_reasons: list[str], fit_reasons: list[str]) -> str:
    job_reason_text = "、".join(job_reasons) if job_reasons else "大きな加点要素なし"
    fit_reason_text = "、".join(fit_reasons) if fit_reasons else "明確な一致要素なし"
    return f"求人属性: {job_reason_text}。マッチ度: {fit_reason_text}。"


def score_jobs(
    input_path: Path,
    output_path: Path,
    limit: int | None = None,
) -> None:
    logger.info("Start scoring jobs")
    logger.info("Input path: %s", input_path)
    logger.info("Output path: %s", output_path)
    logger.info("Limit: %s", limit)

    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Loaded %d rows from CSV", len(rows))

    if limit is not None:
        rows = rows[:limit]
        logger.info("Trimmed rows to %d by limit", len(rows))

    scored_rows = []

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Processing row %d/%d: %s", i, len(rows), title)

        try:
            job_score, job_reasons = calculate_job_score(row)
            fit_score, fit_reasons = calculate_fit_score(row)
            score_reason = build_score_reason(job_reasons, fit_reasons)
            total_score = job_score + fit_score

            new_row = dict(row)
            new_row["job_score"] = job_score
            new_row["fit_score"] = fit_score
            new_row["total_score"] = total_score
            new_row["score_reason"] = score_reason

            scored_rows.append(new_row)

            logger.info("Completed row %d/%d", i, len(rows))

        except Exception as e:
            logger.exception("Failed to score row %d/%d: %s", i, len(rows), e)

    if not scored_rows:
        logger.warning("No scored rows were created. Skip writing output.")
        return

    fieldnames = list(scored_rows[0].keys())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)

    logger.info("Wrote %d rows to %s", len(scored_rows), output_path)


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    limit: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    score_jobs(
        input_path=input_path,
        output_path=output_path,
        limit=limit,
    )


if __name__ == "__main__":
    main(limit=3)