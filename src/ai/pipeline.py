import logging
from pathlib import Path

from src import fetch_list, fetch_detail, build_dataset
from src.ai import summarize, classify, score, compare
from src.user_profile import UserProfile


DEFAULT_URL = "https://job-boards.greenhouse.io/paypay"

DEFAULT_LIST_OUT_PATH = Path("data/raw/list.html")
DEFAULT_DETAIL_DIR = Path("data/raw")

DEFAULT_INPUT_CSV_PATH = Path("data/output/jobs.csv")
DEFAULT_ENRICHED_PATH = Path("data/output/jobs_enriched.csv")
DEFAULT_CLASSIFIED_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_SCORED_PATH = Path("data/output/jobs_scored.csv")
DEFAULT_COMPARED_PATH = Path("data/output/jobs_compared.csv")

DEFAULT_MAX_JOBS = 50

logger = logging.getLogger(__name__)

def run_collection_pipeline(
    url: str = DEFAULT_URL,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
) -> None:
    logger.info("Start collection pipeline")
    logger.info("URL: %s", url)
    logger.info("List out path: %s", list_out_path)
    logger.info("Detail dir: %s", detail_dir)
    logger.info("Jobs CSV path: %s", jobs_csv_path)
    logger.info("Max jobs: %s", max_jobs)

    list_paths = fetch_list.main(
        url= url ,
        out_path= list_out_path ,
    )

    fetch_detail.main(
        list_paths = list_paths ,
        max_jobs= max_jobs ,
    )

    build_dataset.main(
        detail_dir= detail_dir ,
        output_path= jobs_csv_path ,
    )

    logger.info("Collection pipeline completed")



def run_analysis_pipeline(
    user_profile: UserProfile,
    input_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logger.info("Start analysis pipeline")
    logger.info("Input path: %s", input_path)
    logger.info("Enriched path: %s", enriched_path)
    logger.info("Classified path: %s", classified_path)
    logger.info("Scored path: %s", scored_path)
    logger.info("Compared path: %s", compared_path)
    logger.info("Limit: %s", limit)
    logger.info("Sort by: %s", sort_by)
    logger.info("Top: %s", top)

    summarize.main(
        input_path= input_path ,
        output_path= enriched_path ,
        limit= limit ,
    )

    classify.main(
        input_path= enriched_path,
        output_path= classified_path ,
        limit= limit ,
    )

    score.main(
        user_profile= user_profile ,
        input_path= classified_path ,
        output_path= scored_path ,
        limit= limit ,
    )

    compare.main(
        input_path= scored_path ,
        output_path= compared_path ,
        sort_by= sort_by ,
        top= top,
    )

    logger.info("Analysis pipeline completed")



def run_full_pipeline(
    user_profile: UserProfile,
    url: str = DEFAULT_URL,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logger.info("Start full pipeline")

    run_collection_pipeline(
        url= url,
        list_out_path= list_out_path ,
        detail_dir= detail_dir ,
        jobs_csv_path= jobs_csv_path ,
        max_jobs= max_jobs ,
    )

    run_analysis_pipeline(
        user_profile= user_profile ,
        input_path= jobs_csv_path ,
        enriched_path= enriched_path ,
        classified_path= classified_path ,
        scored_path= scored_path ,
        compared_path= compared_path ,
        limit= limit ,
        sort_by= sort_by,
        top= top ,
    )

    logger.info("Full pipeline completed")

def main(
    mode: str,
    user_profile: UserProfile,
    url: str = DEFAULT_URL,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    if mode == "analysis":
        run_analysis_pipeline(
            user_profile= user_profile ,
            input_path= list_out_path ,
            enriched_path= enriched_path ,
            classified_path= classified_path ,
            scored_path= scored_path ,
            compared_path= compared_path ,
            limit= limit ,
            sort_by= sort_by ,
            top= top ,
        )
        return

    if mode == "full":
        run_full_pipeline(
            user_profile= user_profile ,
            url= url ,
            list_out_path= list_out_path ,
            detail_dir= detail_dir ,
            jobs_csv_path= jobs_csv_path ,
            enriched_path= enriched_path ,
            classified_path= classified_path ,
            scored_path= scored_path ,
            compared_path= compared_path ,
            max_jobs= max_jobs ,
            limit= limit ,
            sort_by= sort_by ,
            top= top ,
        )
        return

    raise ValueError(f"Unsupported mode: {mode}")