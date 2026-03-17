# src/parse_list.py

from pathlib import Path
from bs4 import BeautifulSoup

LIST_PATH = Path("data/raw/list.html")


def main():
    # 1. 保存したHTMLを読み込む
    html = LIST_PATH.read_text(encoding="utf-8")

    # 2. BeautifulSoupでDOM化
    soup = BeautifulSoup(html, "lxml")

    # 3. aタグを全部取得
    links = soup.find_all("a", href=True)

    job_links = []

    for a in links:
        href = a["href"]

        # 4. /jobs/ を含むものだけ抽出
        if "/jobs/" in href:
            title = a.get_text(strip=True)
            job_links.append((title, href))

    print("件数:", len(job_links))
    print("サンプル:", job_links[:5])


if __name__ == "__main__":
    main()