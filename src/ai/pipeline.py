import logging
from pathlib import Path

from src import fetch_list, fetch_detail, build_dataset, retry_failed
from src.ai import summarize, classify, score, compare, export_detail, translate
from src.user_profile import UserProfile


DEFAULT_URL = "https://job-boards.greenhouse.io/paypay"

DEFAULT_LIST_OUT_PATH = Path("data/raw/list.html")
DEFAULT_DETAIL_DIR = Path("data/raw")
DEFAULT_INPUT_CSV_PATH = Path("data/output/jobs.csv")
DEFAULT_ENRICHED_PATH = Path("data/output/jobs_enriched.csv")
DEFAULT_CLASSIFIED_PATH = Path("data/output/jobs_classified.csv")
DEFAULT_SCORED_PATH = Path("data/output/jobs_scored.csv")
DEFAULT_COMPARED_PATH = Path("data/output/jobs_compared.csv")
DEFAULT_DETAIL_VIEW_PATH = Path("data/output/jobs_detail_view.csv")
DEFAULT_TRANSLATED_PATH = Path("data/output/jobs_translated.csv")
DEFAULT_MAX_JOBS = 50

logger = logging.getLogger(__name__)

def clear_file_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()
        logger.info("Removed old file: %s", path)

def ensure_has_detail_html(detail_dir: Path) -> None:
    ensure_file_exists(detail_dir, "detail_dir")

    html_files = list(detail_dir.glob("detail_*.html"))
    if not html_files:
        raise ValueError(f"No detail HTML files found in: {detail_dir}")


def ensure_non_empty_list(values: list, label: str) -> None:
    if not values:
        raise RuntimeError(f"{label} is empty")


def ensure_file_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def ensure_non_empty_file(path: Path, label: str) -> None:
    ensure_file_exists(path, label)

    if path.stat().st_size == 0:
        raise RuntimeError(f"{label} is empty: {path}")


def validate_positive_int(value: int | None, label: str) -> None:
    if value is not None and value <= 0:
        raise ValueError(f"{label} must be positive: {value}")

def validate_pipeline_inputs(
    mode: str,
    url: str,
    urls: list[str] | None,
    max_jobs: int,
    limit: int | None,
    top: int | None,
) -> None:
    if mode not in {"full", "analysis"}:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "full":
        has_single_url = bool(url)
        has_multiple_urls = bool(urls)

        if not has_single_url and not has_multiple_urls:
            raise ValueError("full mode requires --url or --urls")

    validate_positive_int(max_jobs, "max_jobs")
    validate_positive_int(limit, "limit")
    validate_positive_int(top, "top")



def run_collection_pipeline(
    url: str = DEFAULT_URL,
    urls: list[str] | None = None,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
) -> None:
    logger.info("Start collection pipeline")
    logger.info("URL: %s", url)
    logger.info("URLs: %s", urls)
    logger.info("List out path: %s", list_out_path)
    logger.info("Detail dir: %s", detail_dir)
    logger.info("Jobs CSV path: %s", jobs_csv_path)
    logger.info("Max jobs: %s", max_jobs)

    validate_positive_int(max_jobs, "max_jobs")

    clear_file_if_exists(fetch_detail.FAIL_LOG)
    clear_file_if_exists(retry_failed.RETRY_FAIL_LOG)
    if urls:
        list_paths = fetch_list.main(
            urls=urls,
            out_dir=list_out_path.parent,
        )
    else:
        list_paths = fetch_list.main(
            url=url,
            out_path=list_out_path,
        )

    ensure_non_empty_list(list_paths, "list_paths")

    processed_urls = fetch_detail.main(
        list_paths=list_paths,
        max_jobs=max_jobs,
    )
    ensure_non_empty_list(processed_urls, "processed_urls")

    retry_result = retry_failed.retry_failed_rows()

    if retry_result.target_count > 0:
        logger.info(
            "Retry was executed: target=%d success=%d failed=%d",
            retry_result.target_count,
            retry_result.success_count,
            retry_result.failed_count,
        )
        if retry_result.failed_count > 0:
            logger.warning(
                "Some detail pages still failed after retry: %d",
                retry_result.failed_count,
            )

    else:
        logger.info("No retry needed")

    ensure_has_detail_html(detail_dir)

    build_dataset.main(
        detail_dir=detail_dir,
        output_path=jobs_csv_path,
    )

    ensure_non_empty_file(jobs_csv_path, "jobs_csv")

    logger.info("Collection pipeline completed")



def run_analysis_pipeline(
    user_profile: UserProfile,
    input_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    detail_view_path: Path = DEFAULT_DETAIL_VIEW_PATH,
    translated_path: Path = DEFAULT_TRANSLATED_PATH,
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
    logger.info("Detail view path: %s", detail_view_path)
    logger.info("Limit: %s", limit)
    logger.info("Sort by: %s", sort_by)
    logger.info("Top: %s", top)

    validate_positive_int(limit, "limit")
    validate_positive_int(top, "top")

    ensure_non_empty_file(input_path, "analysis_input_csv")

    summarize.main(
        input_path=input_path,
        output_path=enriched_path,
        limit=limit,
    )

    ensure_non_empty_file(enriched_path, "enriched_csv")

    translate.main(
        input_path=enriched_path,
        output_path=translated_path,
        limit=limit,
    )

    ensure_non_empty_file(translated_path, "translated_csv")

    classify.main(
        input_path=translated_path,
        output_path=classified_path,
        limit=limit,
    )

    ensure_non_empty_file(classified_path, "classified_csv")

    score.main(
        user_profile=user_profile,
        input_path=classified_path,
        output_path=scored_path,
        limit=limit,
    )

    ensure_non_empty_file(scored_path, "scored_csv")

    compare.main(
        input_path=scored_path,
        output_path=compared_path,
        sort_by=sort_by,
        top=top,
    )

    ensure_non_empty_file(compared_path, "compared_csv")

    export_detail.main(
        input_path=scored_path,
        output_path=detail_view_path,
        sort_by=sort_by,
        top=top
    )

    ensure_non_empty_file(detail_view_path, "detail_view")

    logger.info("Analysis pipeline completed")



def run_full_pipeline(
    user_profile: UserProfile,
    url: str = DEFAULT_URL,
    urls: list[str] | None = None,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    translated_path: Path = DEFAULT_TRANSLATED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    detail_view_path: Path = DEFAULT_DETAIL_VIEW_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logger.info("Start full pipeline")

    run_collection_pipeline(
        url= url,
        urls= urls,
        list_out_path= list_out_path ,
        detail_dir= detail_dir ,
        jobs_csv_path= jobs_csv_path ,
        max_jobs= max_jobs ,
    )

    run_analysis_pipeline(
        user_profile= user_profile ,
        input_path= jobs_csv_path ,
        enriched_path= enriched_path ,
        translated_path= translated_path ,
        classified_path= classified_path ,
        scored_path= scored_path ,
        compared_path= compared_path ,
        detail_view_path=detail_view_path,
        limit= limit ,
        sort_by= sort_by,
        top= top ,
    )

    logger.info("Full pipeline completed")


def main(
    mode: str,
    user_profile: UserProfile,
    url: str = DEFAULT_URL,
    urls: list[str] | None = None,
    list_out_path: Path = DEFAULT_LIST_OUT_PATH,
    detail_dir: Path = DEFAULT_DETAIL_DIR,
    jobs_csv_path: Path = DEFAULT_INPUT_CSV_PATH,
    enriched_path: Path = DEFAULT_ENRICHED_PATH,
    classified_path: Path = DEFAULT_CLASSIFIED_PATH,
    scored_path: Path = DEFAULT_SCORED_PATH,
    compared_path: Path = DEFAULT_COMPARED_PATH,
    detail_view_path: Path = DEFAULT_DETAIL_VIEW_PATH,
    translate_csv_path: Path = DEFAULT_TRANSLATED_PATH,
    max_jobs: int = DEFAULT_MAX_JOBS,
    limit: int | None = None,
    sort_by: str = "total_score",
    top: int | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    try:
        validate_pipeline_inputs(
            mode=mode,
            url=url,
            urls=urls,
            max_jobs=max_jobs,
            limit=limit,
            top=top,
        )

        if mode == "analysis":
            run_analysis_pipeline(
                user_profile=user_profile,
                input_path=jobs_csv_path,
                enriched_path=enriched_path,
                translated_path=translate_csv_path,
                classified_path=classified_path,
                scored_path=scored_path,
                compared_path=compared_path,
                detail_view_path=detail_view_path,
                limit=limit,
                sort_by=sort_by,
                top=top,
            )
            return

        if mode == "full":
            run_full_pipeline(
                user_profile=user_profile,
                url=url,
                urls=urls,
                list_out_path=list_out_path,
                detail_dir=detail_dir,
                jobs_csv_path=jobs_csv_path,
                enriched_path=enriched_path,
                translated_path=translate_csv_path,
                classified_path=classified_path,
                scored_path=scored_path,
                compared_path=compared_path,
                detail_view_path=detail_view_path,
                max_jobs=max_jobs,
                limit=limit,
                sort_by=sort_by,
                top=top,
            )
            return

        raise ValueError(f"Unsupported mode: {mode}")

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        raise

