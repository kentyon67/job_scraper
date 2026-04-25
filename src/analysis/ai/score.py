import csv
import logging
from pathlib import Path

from src.user_profile import UserProfile


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

ENTRY_EMPLOYMENT_TYPES = {"Internship", "NewGrad"}
ENTRY_LEVEL_HINTS = {"Beginner"}

HIGH_VALUE_CATEGORIES = {
    "AI/ML": 25,
    "Data": 22,
    "Backend": 20,
    "Infra/SRE": 18,
    "Security": 18,
    "Frontend": 12,
    "Mobile": 12,
    "Product": 10,
    "Other": 5,
}


def split_pipe_values(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in str(text).split("|") if part.strip()]


def contains_any_keyword(text: str, keywords: list[str]) -> bool:
    lower_text = text.lower()
    return any(keyword in lower_text for keyword in keywords)


def parse_bool_yes_no(value: str) -> bool:
    return str(value).strip().lower() == "yes"


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


def calculate_job_score(row: dict) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    job_category = row.get("job_category", "")
    ai_related = row.get("ai_related", "")
    work_style = row.get("work_style", "")
    employment_type = row.get("employment_type", "")
    experience_level_hint = row.get("experience_level_hint", "")
    global_related = row.get("global_related", "")
    language_tags = split_pipe_values(row.get("language_tags", ""))
    tech_keywords = split_pipe_values(row.get("tech_keywords", ""))

    description = row.get("description", "")
    qualifications = row.get("qualifications", "")
    working_condition = row.get("working_condition", "")
    ai_summary = row.get("ai_summary", "")
    location = row.get("location", "")

    combined_text = " ".join(
        [description, qualifications, working_condition, ai_summary, location]
    ).lower()

    category_score = HIGH_VALUE_CATEGORIES.get(job_category, 5)
    score += category_score
    reasons.append(f"{job_category or 'Other'}カテゴリ")

    if parse_bool_yes_no(ai_related):
        score += 15
        reasons.append("AI関連")

    if parse_bool_yes_no(global_related) or contains_any_keyword(combined_text, GLOBAL_KEYWORDS):
        score += 15
        reasons.append("グローバル要素あり")

    if work_style == "Remote":
        score += 15
        reasons.append("リモート勤務")
    elif work_style == "Hybrid":
        score += 10
        reasons.append("ハイブリッド勤務")
    elif work_style == "Onsite":
        score += 4
        reasons.append("出社勤務")

    if employment_type in ENTRY_EMPLOYMENT_TYPES:
        score += 12
        reasons.append("応募しやすい雇用形態")

    if experience_level_hint in ENTRY_LEVEL_HINTS:
        score += 10
        reasons.append("初学者向けの可能性")

    if language_tags:
        score += min(len(language_tags) * 2, 8)
        reasons.append("技術スタック情報あり")

    if tech_keywords:
        score += min(len(tech_keywords) * 2, 10)
        reasons.append("主要技術キーワードあり")

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


def calculate_fit_score(
    row: dict,
    user_profile: UserProfile | None,
) -> tuple[int, list[str]]:
    if user_profile is None:
        return 0, ["プロフィール未設定のためfit_score未計算"]

    score = 0
    reasons: list[str] = []

    language_tags = [normalize_text(x) for x in split_pipe_values(row.get("language_tags", ""))]
    tech_keywords = [normalize_text(x) for x in split_pipe_values(row.get("tech_keywords", ""))]
    job_category = normalize_text(row.get("job_category", ""))
    work_style = row.get("work_style", "")
    employment_type = row.get("employment_type", "")
    experience_level_hint = row.get("experience_level_hint", "")
    global_related = row.get("global_related", "")
    location = normalize_text(row.get("location", ""))

    preferred_languages = [normalize_text(x) for x in user_profile.get("preferred_languages", [])]
    preferred_domains = [normalize_text(x) for x in user_profile.get("preferred_domains", [])]
    prefer_global = user_profile.get("prefer_global", False)
    experience_level = normalize_text(user_profile.get("experience_level", "beginner"))
    priority_mode = normalize_text(user_profile.get("priority_mode", "growth"))
    preferred_locations = [normalize_text(x) for x in user_profile.get("preferred_locations", [])]
    allow_remote = user_profile.get("allow_remote", False)

    matched_languages = [lang for lang in preferred_languages if lang in language_tags]
    if matched_languages:
        score += min(10 * len(matched_languages), 25)
        reasons.append(f"希望言語と一致: {', '.join(matched_languages)}")

    if job_category in preferred_domains:
        score += 25
        reasons.append("希望領域と一致")

    if prefer_global and parse_bool_yes_no(global_related):
        score += 15
        reasons.append("グローバル志向と一致")

    if experience_level == "beginner":
        if experience_level_hint == "Beginner":
            score += 20
            reasons.append("初学者向けと一致")
        elif employment_type in ENTRY_EMPLOYMENT_TYPES:
            score += 12
            reasons.append("応募しやすい雇用形態")
        else:
            if priority_mode == "growth":
                score += 6
                reasons.append("背伸び枠として挑戦価値あり")
            elif priority_mode == "realistic":
                score -= 5
                reasons.append("現実性重視ではやや不一致")

    elif experience_level == "intermediate":
        if experience_level_hint == "Intermediate":
            score += 15
            reasons.append("中級レベルと一致")
        elif experience_level_hint == "Beginner":
            score += 8
            reasons.append("取り組みやすい難易度")

    elif experience_level == "advanced":
        if experience_level_hint == "Advanced":
            score += 18
            reasons.append("上級レベルと一致")
        elif priority_mode == "growth":
            score += 5
            reasons.append("役割拡張の余地あり")

    location_match = any(loc and loc in location for loc in preferred_locations)
    is_remote = work_style == "Remote"
    is_hybrid = work_style == "Hybrid"

    if location_match:
        score += 15
        reasons.append("希望勤務地と一致")
    elif allow_remote and is_remote:
        score += 12
        reasons.append("リモート許容条件と一致")
    elif allow_remote and is_hybrid:
        score += 8
        reasons.append("ハイブリッド勤務と相性あり")
    else:
        score -= 5
        reasons.append("勤務地条件がやや不一致")

    if priority_mode == "growth":
        if parse_bool_yes_no(row.get("ai_related", "")):
            score += 8
            reasons.append("成長性の高い分野")
        if tech_keywords:
            score += 5
            reasons.append("技術的な広がりあり")

    elif priority_mode == "balanced":
        score += 5
        reasons.append("バランス重視設定")

    elif priority_mode == "realistic":
        if employment_type in ENTRY_EMPLOYMENT_TYPES or experience_level_hint == "Beginner":
            score += 10
            reasons.append("現実的に狙いやすい")
        else:
            score -= 3
            reasons.append("現実性重視ではやや難しめ")

    return max(0, min(score, 100)), reasons


def build_score_reason(job_reasons: list[str], fit_reasons: list[str]) -> str:
    job_reason_text = "、".join(job_reasons) if job_reasons else "大きな加点要素なし"
    fit_reason_text = "、".join(fit_reasons) if fit_reasons else "明確な一致要素なし"
    return f"求人属性: {job_reason_text}。マッチ度: {fit_reason_text}。"


def build_short_reason(row: dict, job_reasons: list[str], fit_reasons: list[str]) -> str:
    parts: list[str] = []

    company_name = row.get("company_name", "")
    job_category = row.get("job_category", "")
    work_style = row.get("work_style", "")
    employment_type = row.get("employment_type", "")
    language_tags = split_pipe_values(row.get("language_tags", ""))

    if company_name:
        parts.append(company_name)
    if job_category:
        parts.append(job_category)
    if work_style and work_style != "Unknown":
        parts.append(work_style)
    if employment_type and employment_type != "Unknown":
        parts.append(employment_type)
    if language_tags:
        parts.append("/".join(language_tags[:3]))

    if len(parts) < 3:
        merged_reasons = job_reasons[:2] + fit_reasons[:2]
        parts.extend(merged_reasons[: 4 - len(parts)])

    return " | ".join(parts[:4])


def score_row(
    row: dict[str, str],
    user_profile: UserProfile | None = None,
) -> dict[str, str]:
    job_score, job_reasons = calculate_job_score(row)
    fit_score, fit_reasons = calculate_fit_score(row, user_profile=user_profile)
    total_score =  job_score + fit_score

    new_row = dict(row)
    new_row["job_score"] = str(job_score)
    new_row["fit_score"] = str(fit_score)
    new_row["total_score"] = str(total_score)
    new_row["score_reason"] = build_score_reason(job_reasons, fit_reasons)
    new_row["short_reason"] = build_short_reason(new_row, job_reasons, fit_reasons)
    return new_row


def score_rows(
    rows: list[dict[str, str]],
    user_profile: UserProfile | None = None,
) -> list[dict[str, str]]:
    return [score_row(row, user_profile=user_profile) for row in rows]


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
    logger.info("Profile mode: %s", "with_profile" if user_profile else "job_score_only")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if limit is not None:
        rows = rows[:limit]

    if not rows:
        raise ValueError("No rows found in input CSV")

    scored_rows = score_rows(rows, user_profile=user_profile)

    fieldnames = list(scored_rows[0].keys())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)

    logger.info("Scoring completed: rows=%d", len(scored_rows))


def main(
    input_path: Path = DEFAULT_INPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    user_profile: UserProfile | None = None,
    limit: int | None = None,
) -> None:
    score_jobs(
        input_path=input_path,
        output_path=output_path,
        user_profile=user_profile,
        limit=limit,
    )


if __name__ == "__main__":
    main()