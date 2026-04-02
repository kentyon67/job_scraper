import logging
from pathlib import Path

from src.ai import summarize, classify, score, compare
from src.user_profile import UserProfile


DEFAULT_INPUT_PATH = Path("data/output/jobs.csv")
DEFAULT_ENRICHED_PATH = Path("data/output/jobs_enriched.csv")
DEFAULT_CLASSIFIED_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_SCORED_PATH = Path("data/output/jobs_scored.csv")
DEFAULT_COMPARED_PATH = Path("data/output/jobs_compared.csv")

logger = logging.getLogger(__name__)


def run_pipeline(
    user_profile: UserProfile,
    input_path: Path = DEFAULT_INPUT_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logger.info("Start pipeline")
    logger.info("Input path: %s", input_path)
    logger.info("Enriched path: %s", enriched_path)
    logger.info("Classified path: %s", classified_path)
    logger.info("Scored path: %s", scored_path)
    logger.info("Compared path: %s", compared_path)
    logger.info("Limit: %s", limit)
    logger.info("Sort by: %s", sort_by)
    logger.info("Top: %s", top)

    summarize.main(
        input_path=input_path,
        output_path=enriched_path,
        limit=limit,
    )

    classify.main(
        input_path=enriched_path,
        output_path=classified_path,
        limit=limit,
    )

    score.main(
        user_profile=user_profile,
        input_path=classified_path,
        output_path=scored_path,
        limit=limit,
    )

    compare.main(
        input_path=scored_path,
        output_path=compared_path,
        sort_by=sort_by,
        top=top,
    )

    logger.info("Pipeline completed")


def main(
    user_profile: UserProfile,
    input_path: Path = DEFAULT_INPUT_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    run_pipeline(
        user_profile=user_profile,
        input_path=input_path,
        enriched_path=enriched_path,
        classified_path=classified_path,
        scored_path=scored_path,
        compared_path=compared_path,
        limit=limit,
        sort_by=sort_by,
        top=top,
    )


if __name__ == "__main__":
    from src.user_profile import DEFAULT_USER_PROFILE

    main(user_profile=DEFAULT_USER_PROFILE, limit=3, top=3)