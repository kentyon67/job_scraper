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
        help="URL取得から比較まで一括実行する",
    )

    pipeline_parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "analysis"],
        help="full: URL取得から比較まで / analysis: CSV分析部分のみ",
    )

    pipeline_parser.add_argument(
        "--url",
        default="https://job-boards.greenhouse.io/paypay",
        help="求人一覧ページのURL",
    )

    pipeline_parser.add_argument(
        "--list-output",
        default="data/raw/list.html",
        help="一覧HTMLの保存先パス",
    )

    pipeline_parser.add_argument(
        "--detail-dir",
        default="data/raw",
        help="詳細HTML保存ディレクトリ",
    )

    pipeline_parser.add_argument(
        "--jobs-output",
        default="data/output/jobs.csv",
        help="buildで出力するCSVパス",
    )

    pipeline_parser.add_argument(
        "--enriched-output",
        default="data/output/jobs_enriched.csv",
        help="summarize出力CSVのパス",
    )

    pipeline_parser.add_argument(
        "--classified-output",
        default="data/output/jobs_classified.csv",
        help="classify出力CSVのパス",
    )

    pipeline_parser.add_argument(
        "--scored-output",
        default="data/output/jobs_scored.csv",
        help="score出力CSVのパス",
    )

    pipeline_parser.add_argument(
        "--compared-output",
        default="data/output/jobs_compared.csv",
        help="compare出力CSVのパス",
    )

    pipeline_parser.add_argument(
        "--max-jobs",
        type=int,
        default=50,
        help="詳細取得する求人件数の上限",
    )

    pipeline_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="分析ステップで処理する件数の上限",
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

    # user_profile 用
    pipeline_parser.add_argument(
        "--lang",
        nargs="+",
        default=None,
        help="希望言語（例: python sql）",
    )

    pipeline_parser.add_argument(
        "--domain",
        nargs="+",
        default=None,
        help="希望領域（例: backend ai data）",
    )

    pipeline_parser.add_argument(
        "--global-flag",
        action="store_true",
        help="グローバル志向なら指定",
    )

    pipeline_parser.add_argument(
        "--exp",
        default=None,
        help="経験レベル（例: beginner intermediate advanced）",
    )

    pipeline_parser.add_argument(
        "--mode-profile",
        dest="mode_profile",
        default=None,
        help="priority_mode（例: growth balanced realistic）",
    )

    pipeline_parser.add_argument(
        "--loc",
        nargs="+",
        default=None,
        help="希望勤務地（例: tokyo osaka remote）",
    )

    pipeline_parser.add_argument(
        "--remote",
        action="store_true",
        help="リモート勤務を許容するなら指定",
    )


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

            mode=args.mode,
            user_profile=user_profile,
            url=args.url,
            list_out_path=Path(args.list_output),
            detail_dir=Path(args.detail_dir),
            jobs_csv_path=Path(args.jobs_output),
            enriched_path=Path(args.enriched_output),
            classified_path=Path(args.classified_output),
            scored_path=Path(args.scored_output),
            compared_path=Path(args.compared_output),
            max_jobs=args.max_jobs,
            limit=args.limit,
            sort_by=args.sort_by,
            top=args.top,
        )

if __name__ == "__main__":
    main()