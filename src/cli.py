import argparse
from pathlib import Path
from src import fetch_list, fetch_detail, retry_failed, build_dataset
from src.user_profile import build_user_profile_from_args
from src.ai import summarize, classify, score, compare, pipeline

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="job_scraper",
        description="Greenhouse求人情報を収集・整形するCLIツール",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="実行するコマンド",
    )

    subparsers.add_parser(
        "fetch-list",
        help="求人一覧ページのHTMLを取得して保存する",
    )

    fetch_detail_parser = subparsers.add_parser(
        "fetch-detail",
        help="求人詳細ページのHTMLを取得して保存する",
    )
    fetch_detail_parser.add_argument(
        "--max-jobs",
        type=int,
        default=fetch_detail.DEFAULT_MAX_JOBS,
        help="取得する求人詳細ページ数の上限",
    )

    retry_parser = subparsers.add_parser(
        "retry",
        help="失敗したURLを再取得する",
    )
    retry_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="再取得する失敗URL件数の上限",
    )

    subparsers.add_parser(
        "build",
        help="保存済みHTMLからCSVを生成する",
    )

    summarize_purser = subparsers.add_parser(
        "summarize",
        help="保存済みCSVからAI要約つきのCSVを作成する"
    )

    summarize_purser.add_argument(
        "--limit",
        type = int ,
        default = None
    )

    summarize_purser.add_argument(
        "--input",
        default="data/output/jobs.csv"
    )

    summarize_purser.add_argument(
        "--output",
        default="data/output/jobs_enriched.csv"
    )


    classify_parser = subparsers.add_parser(
        "classify",
        help="AI分類つきのCSVを作成する",
    )
    classify_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="分類する件数の上限",
    )
    classify_parser.add_argument(
        "--input",
        default="data/output/jobs_enriched.csv",
        help="入力CSVのパス",
    )
    classify_parser.add_argument(
        "--output",
        default="data/output/jobs_classified.csv",
        help="出力CSVのパス",
    )

    score_parser = subparsers.add_parser(
        "score",
        help="AI分類済みCSVからスコアつきCSVを作成する",
    )

    score_parser.add_argument(
        "--input",
        default="data/output/jobs_classified.csv",
        help="入力CSVのパス",
    )
    score_parser.add_argument(
        "--output",
        default="data/output/jobs_scored.csv",
        help="出力CSVのパス",
    )
    score_parser.add_argument("--lang", nargs="+", default=None)
    score_parser.add_argument("--domain", nargs="+", default=None)
    score_parser.add_argument("--global-flag", action="store_true")
    score_parser.add_argument("--exp", default=None)
    score_parser.add_argument("--mode", default=None)
    score_parser.add_argument("--loc", nargs="+", default=None)
    score_parser.add_argument("--remote", action="store_true")
    score_parser.add_argument("--limit", type=int, default=None)

    compare_parser = subparsers.add_parser(
        "compare",
        help="スコア済みCSVを比較用に並び替えて出力する",
    )
    compare_parser.add_argument(
        "--input",
        default="data/output/jobs_scored.csv",
        help="入力CSVのパス",
    )
    compare_parser.add_argument(
        "--output",
        default="data/output/jobs_compared.csv",
        help="出力CSVのパス",
    )
    compare_parser.add_argument(
        "--sort-by",
        default="total_score",
        choices=["total_score", "job_score", "fit_score"],
        help="並び替え基準",
    )
    compare_parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="上位何件を出力するか",
    )

    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="要約・分類・スコアリング・比較を一括実行する",
    )

    pipeline_parser.add_argument(
        "--input",
        default="data/output/jobs.csv",
        help="入力CSVのパス",
    )
    pipeline_parser.add_argument(
        "--enriched-output",
        default="data/output/jobs_enriched.csv",
        help="要約出力CSVのパス",
    )
    pipeline_parser.add_argument(
        "--classified-output",
        default="data/output/jobs_classified.csv",
        help="分類出力CSVのパス",
    )
    pipeline_parser.add_argument(
        "--scored-output",
        default="data/output/jobs_scored.csv",
        help="スコア出力CSVのパス",
    )
    pipeline_parser.add_argument(
        "--compared-output",
        default="data/output/jobs_compared.csv",
        help="比較出力CSVのパス",
    )
    pipeline_parser.add_argument(
        "--sort-by",
        default="total_score",
        choices=["total_score", "job_score", "fit_score"],
        help="compareの並び替え基準",
    )
    pipeline_parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="compareで出力する上位件数",
    )
    pipeline_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="各ステップで処理する件数の上限",
    )

    pipeline_parser.add_argument("--lang", nargs="+", default=None)
    pipeline_parser.add_argument("--domain", nargs="+", default=None)
    pipeline_parser.add_argument("--global-flag", action="store_true")
    pipeline_parser.add_argument("--exp", default=None)
    pipeline_parser.add_argument("--mode", default=None)
    pipeline_parser.add_argument("--loc", nargs="+", default=None)
    pipeline_parser.add_argument("--remote", action="store_true")



    args = parser.parse_args()




    if args.command == "fetch-list":
        fetch_list.main()

    elif args.command == "fetch-detail":
        fetch_detail.main(max_jobs=args.max_jobs)

    elif args.command == "retry":
        retry_failed.main(limit=args.limit)

    elif args.command == "build":
        build_dataset.main()

    elif args.command == "summarize":
        summarize.main(
        input_path = Path(args.input),
        output_path = Path(args.output),
        limit=args.limit,
    )

    elif args.command == "classify":
        classify.main(
            input_path=Path(args.input),
            output_path=Path(args.output),
            limit=args.limit,
        )

    elif args.command == "score":
        user_profile = build_user_profile_from_args(args)

        score.main(
            input_path=Path(args.input),
            output_path=Path(args.output),
            limit=args.limit,
            user_profile=user_profile,
        )

    elif args.command == "compare":
        compare.main(
            input_path=Path(args.input),
            output_path=Path(args.output),
            sort_by=args.sort_by,
            top=args.top,
        )

    elif args.command == "pipeline":
        user_profile = build_user_profile_from_args(args)

        pipeline.main(
            user_profile= user_profile,
            input_path=Path(args.input),
            enriched_path=Path(args.enriched_output),
            classified_path=Path(args.classified_output),
            scored_path=Path(args.scored_output),
            compared_path=Path(args.compared_output),
            limit= args.limit,
            sort_by= args.sort_by,
            top= args.top,
        )
if __name__ == "__main__":
    main()