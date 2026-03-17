# src/fetch_list.py
from pathlib import Path
import requests

URL = "https://job-boards.greenhouse.io/paypay"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

TIMEOUT = 20  # 秒

OUT_PATH = Path("../data/raw/list.html")


def main() -> None:
    # 1) HTTPで一覧ページHTMLを取る
    resp = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)

    # 2) 200番台以外（404/500など）ならここでエラーにする
    resp.raise_for_status()

    html = resp.text

    # 3) 保存先フォルダが無ければ作る
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 4) HTMLをファイルとして保存
    OUT_PATH.write_text(html, encoding="utf-8")

    print(f"[OK] saved: {OUT_PATH} (chars={len(html)})")


if __name__ == "__main__":
    main()