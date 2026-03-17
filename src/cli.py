import argparse

from src import fetch_list, fetch_detail, retry_failed, build_dataset


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
        default=50,
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

    args = parser.parse_args()

    if args.command == "fetch-list":
        fetch_list.main()

    elif args.command == "fetch-detail":
        fetch_detail.main(max_jobs=args.max_jobs)

    elif args.command == "retry":
        retry_failed.main(limit=args.limit)

    elif args.command == "build":
        build_dataset.main()


if __name__ == "__main__":
    main()