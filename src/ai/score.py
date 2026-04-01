import csv
import logging
from pathlib import Path
from src.user_profile import DEFAULT_USER_PROFILE, UserProfile


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

    job_category = row.get("job_category", "")
    ai_related = row.get("ai_related", "")
    location = row.get("location", "")
    ai_summary = row.get("ai_summary", "")
    qualifications = row.get("qualifications", "")
    description = row.get("description", "")
    working_condition = row.get("working_condition", "")

    job_category_normalized = job_category.strip().lower()
    ai_related_normalized = ai_related.strip().lower()

    combined_text = " ".join(
        [ai_summary, qualifications, description, working_condition, location]
    ).lower()

    category_scores = {
        "ai/ml": 25,
        "data": 22,
        "backend": 20,
        "infra/sre": 18,
        "security": 18,
        "frontend": 12,
        "mobile": 12,
        "product": 10,
        "other": 5,
    }

    category_score = category_scores.get(job_category_normalized, 5)
    score += category_score
    reasons.append(f"{job_category or 'other'}カテゴリ")

    if ai_related_normalized == "yes":
        score += 15
        reasons.append("AI関連")

    if contains_any_keyword(combined_text, GLOBAL_KEYWORDS):
        score += 20
        reasons.append("英語・グローバル要素あり")

    if "remote" in combined_text or "フルリモート" in combined_text:
        score += 15
        reasons.append("リモート可")
    elif "hybrid" in combined_text or "ハイブリッド" in combined_text:
        score += 10
        reasons.append("ハイブリッド勤務")
    elif "flex" in combined_text or "flexible" in combined_text or "フレックス" in combined_text:
        score += 8
        reasons.append("柔軟な勤務形態")

    if contains_any_keyword(combined_text, ENTRY_KEYWORDS):
        score += 10
        reasons.append("エントリーしやすい可能性")

    text_volume = len(combined_text.strip())

    if text_volume >= 800:
        score += 15
        reasons.append("情報量が豊富")
    elif text_volume >= 400:
        score += 10
        reasons.append("情報量が十分")
    elif text_volume >= 200:
        score += 5
        reasons.append("最低限の情報あり")

    return min(score, 100), reasons


def calculate_fit_score(row: dict, user_profile: UserProfile) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    python_related = row.get("python_related", "")
    ai_related = row.get("ai_related", "")
    job_category = row.get("job_category", "")
    location = row.get("location", "")
    ai_summary = row.get("ai_summary", "")
    qualifications = row.get("qualifications", "")
    description = row.get("description", "")

    python_related_normalized = python_related.strip().lower()
    ai_related_normalized = ai_related.strip().lower()
    job_category_normalized = job_category.strip().lower()
    lower_location = location.lower()

    combined_text = " ".join([ai_summary, qualifications, description, location]).lower()

    preferred_languages = user_profile.get("preferred_languages", [])
    preferred_domains = user_profile.get("preferred_domains", [])
    prefer_global = user_profile.get("prefer_global", False)
    experience_level = user_profile.get("experience_level", "beginner")
    priority_mode = user_profile.get("priority_mode", "balanced")
    preferred_locations = user_profile.get("preferred_locations", [])
    allow_remote = user_profile.get("allow_remote", False)

    if "python" in preferred_languages and python_related_normalized == "yes":
        score += 20
        reasons.append("希望言語pythonと一致")

    if job_category_normalized in preferred_domains:
        score += 25
        reasons.append(f"希望領域{job_category}と一致")

    if "ai/ml" in preferred_domains and ai_related_normalized == "yes":
        score += 15
        reasons.append("AI志向と一致")

    has_global_signal = contains_any_keyword(combined_text, GLOBAL_KEYWORDS)
    if prefer_global and has_global_signal:
        score += 15
        reasons.append("グローバル志向と一致")

    has_entry_signal = contains_any_keyword(combined_text, ENTRY_KEYWORDS)

    if experience_level == "beginner":
        if has_entry_signal:
            score += 20
            reasons.append("初学者向け要素あり")
        else:
            if priority_mode == "growth":
                score += 8
                reasons.append("背伸び枠として挑戦余地あり")
            elif priority_mode == "realistic":
                score -= 5
                reasons.append("現実性重視ではやや不一致")

    elif experience_level == "intermediate":
        if has_entry_signal:
            score += 10
            reasons.append("比較的取り組みやすい")
        else:
            score += 12
            reasons.append("中級者向けとして妥当")

    elif experience_level == "advanced":
        if not has_entry_signal:
            score += 15
            reasons.append("経験者向け案件と一致")
        else:
            if priority_mode == "growth":
                score += 5
                reasons.append("役割拡張の余地あり")

    if priority_mode == "growth":
        if ai_related_normalized == "yes":
            score += 10
            reasons.append("成長性の高い領域")
        if not has_entry_signal:
            score += 5
            reasons.append("挑戦価値あり")

    elif priority_mode == "balanced":
        score += 5
        reasons.append("バランス重視設定")

    elif priority_mode == "realistic":
        if has_entry_signal:
            score += 10
            reasons.append("現実的に狙いやすい")
        else:
            score -= 3
            reasons.append("現実性重視ではやや難しめ")

    location_match = False
    for loc in preferred_locations:
        if loc in lower_location:
            location_match = True
            break

    is_remote = ("remote" in lower_location) or ("リモート" in lower_location)

    if location_match:
        score += 15
        reasons.append("希望勤務地と一致")
    elif allow_remote and is_remote:
        score += 12
        reasons.append("リモート許容条件と一致")
    else:
        score -= 5
        reasons.append("勤務地条件がやや不一致")

    return max(0, min(score, 100)), reasons


def build_score_reason(job_reasons: list[str], fit_reasons: list[str]) -> str:
    job_reason_text = "、".join(job_reasons) if job_reasons else "大きな加点要素なし"
    fit_reason_text = "、".join(fit_reasons) if fit_reasons else "明確な一致要素なし"
    return f"求人属性: {job_reason_text}。マッチ度: {fit_reason_text}。"


def score_jobs(
    input_path: Path,
    output_path: Path,
    user_profile: UserProfile | None = None,
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
    if user_profile is None:
        user_profile = DEFAULT_USER_PROFILE

    for i, row in enumerate(rows, start=1):
        title = row.get("title", "")
        logger.info("Processing row %d/%d: %s", i, len(rows), title)

        try:
            job_score, job_reasons = calculate_job_score(row)
            fit_score, fit_reasons = calculate_fit_score(row, user_profile)
            total_score = job_score + fit_score
            score_reason = build_score_reason(job_reasons, fit_reasons)

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
    user_profile: UserProfile,
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
        user_profile=user_profile,
        limit=limit,
    )


if __name__ == "__main__":
    main(user_profile=DEFAULT_USER_PROFILE, limit=3)