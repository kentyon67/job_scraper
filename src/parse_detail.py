# src/parse_detail.py
from pathlib import Path
from bs4 import BeautifulSoup, Tag

DETAIL_PATH = Path("data/raw/detail_0.html")


def text_or_empty(tag: Tag | None) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def extract_sections(soup: BeautifulSoup) -> dict[str, str]:
    """
    見出し(h2/h3) -> その見出しの本文（次の見出しまで）を集める
    """
    sections: dict[str, str] = {}

    # 本文がまとまっていそうな場所（無ければbody全体）
    container = (
        soup.select_one(".job__description")
        or soup.select_one("#content")
        or soup.body
        or soup
    )

    headings = container.find_all(["h2", "h3"])
    for h in headings:
        key = h.get_text(" ", strip=True)
        if not key:
            continue

        parts: list[str] = []
        cur = h.next_sibling

        while cur is not None:
            # 次の見出しが来たら、そのセクションは終了
            if isinstance(cur, Tag) and cur.name in ["h2", "h3"]:
                break

            if isinstance(cur, Tag):
                # よく本文が入るタグを拾う
                if cur.name in ["p", "ul", "ol"]:
                    txt = cur.get_text(" ", strip=True)
                    if txt:
                        parts.append(txt)

                # divの中にp/ulが入ってることがあるので拾う
                elif cur.name == "div":
                    for t in cur.find_all(["p", "ul", "ol"], recursive=True):
                        txt = t.get_text(" ", strip=True)
                        if txt:
                            parts.append(txt)

            cur = cur.next_sibling

        # 重複っぽいものを軽く除去して結合
        uniq = list(dict.fromkeys(parts))
        value = "\n".join(uniq).strip()

        if value:
            sections[key] = value

    return sections


def main() -> None:
    html = DETAIL_PATH.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    title = text_or_empty(soup.find("h1"))
    location = text_or_empty(soup.select_one(".job__location"))

    sections = extract_sections(soup)

    print("[title]", title)
    print("[location]", location)

    print("\n[sections keys]")
    for k in list(sections.keys())[:20]:
        print("-", k)

    # 1個だけ中身サンプル表示（長すぎ防止）
    if sections:
        first_key = next(iter(sections))
        print(f"\n[sample: {first_key}]")
        print(sections[first_key][:500])


if __name__ == "__main__":
    main()