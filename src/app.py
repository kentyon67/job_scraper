import pandas as pd
import streamlit as st


LIST_PATH = "data/output/jobs_compared.csv"
DETAIL_PATH = "data/output/jobs_detail_view.csv"


def load_list_data() -> pd.DataFrame:
    df_list = pd.read_csv(LIST_PATH).fillna("")
    return df_list


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #111827 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 28px 28px 20px 28px;
            margin-bottom: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 1rem;
            color: #cbd5e1;
            line-height: 1.7;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: white;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .metric-chip-wrap {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 12px 0 6px 0;
        }

        .metric-chip {
            background: rgba(255,255,255,0.08);
            color: #e5e7eb;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.9rem;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .rank-pill {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
            color: #111827;
            font-weight: 900;
            font-size: 0.95rem;
            padding: 7px 12px;
            border-radius: 999px;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .badge-category {
            background: #2563eb;
            color: white;
        }

        .badge-location {
            background: #10b981;
            color: #052e16;
        }

        .card-title {
            font-size: 1.08rem;
            font-weight: 800;
            color: white;
            margin-top: 4px;
            margin-bottom: 10px;
            line-height: 1.5;
        }

        .muted {
            color: #94a3b8;
            font-size: 0.92rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
            padding: 10px 12px;
            border-radius: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_category(value: str) -> str:
    mapping = {
        "AI/ML": "AI・機械学習",
        "Data": "データ",
        "Backend": "バックエンド",
        "Frontend": "フロントエンド",
        "Infra/SRE": "インフラ / SRE",
        "Security": "セキュリティ",
        "Mobile": "モバイル",
        "Product": "プロダクト",
        "Other": "その他",
    }
    return mapping.get(str(value), str(value))


def normalize_location(value: str) -> str:
    mapping = {
        "Hybrid": "ハイブリッド",
        "Remote": "リモート",
        "Onsite": "出社",
    }
    return mapping.get(str(value), str(value))


def render_hero(df_list: pd.DataFrame) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">JobFit</div>
            <div class="hero-subtitle">
                求人をAIで整理して、あなたに合いそうな仕事を見つけやすくするアプリです。<br>
                カード一覧で比較して、気になる求人だけ詳しく確認できます。
            </div>
            <div class="metric-chip-wrap">
                <div class="metric-chip">掲載件数: {len(df_list)}件</div>
                <div class="metric-chip">AI要約つき</div>
                <div class="metric-chip">一覧 + 詳細ページ対応</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filters(df_list: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("絞り込み")

    categories = ["すべて"] + sorted(
        [normalize_category(c) for c in df_list["job_category"].astype(str).unique().tolist() if c]
    )
    selected_category = st.sidebar.selectbox("職種カテゴリ", categories)

    locations = ["すべて"] + sorted(
        [normalize_location(l) for l in df_list["location"].astype(str).unique().tolist() if l]
    )
    selected_location = st.sidebar.selectbox("勤務地", locations)

    keyword = st.sidebar.text_input("タイトル検索")
    min_score = st.sidebar.slider("最低総合スコア", 0, 100, 0, 1)

    filtered = df_list.copy()

    if selected_category != "すべて":
        filtered = filtered[
            filtered["job_category"].astype(str).apply(normalize_category) == selected_category
        ]

    if selected_location != "すべて":
        filtered = filtered[
            filtered["location"].astype(str).apply(normalize_location) == selected_location
        ]

    if keyword.strip():
        filtered = filtered[
            filtered["title"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    filtered = filtered[
        pd.to_numeric(filtered["total_score"], errors="coerce").fillna(0) >= min_score
    ]

    return filtered


def render_job_card(row: pd.Series) -> bool:
    total_score = int(float(row.get("total_score", 0) or 0))
    fit_score = int(float(row.get("fit_score", 0) or 0))
    job_score = int(float(row.get("job_score", 0) or 0))

    with st.container(border=True):
        st.markdown(
            f"""
            <div>
                <span class="rank-pill">#{row.get('rank', '')}</span>
                <span class="badge badge-category">{normalize_category(row.get('job_category', ''))}</span>
                <span class="badge badge-location">{normalize_location(row.get('location', ''))}</span>
                <div class="card-title">{row.get('title', '')}</div>
                <div class="muted">注目ポイント: {row.get('short_reason', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総合", total_score)
        with col2:
            st.metric("マッチ度", fit_score)
        with col3:
            st.metric("求人価値", job_score)

        st.progress(total_score / 100)

        return st.button(
            "詳細を見る",
            key=f"detail_btn_{row.get('url', '')}",
            use_container_width=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="JobFit",
        page_icon="💼",
        layout="wide",
    )

    inject_css()

    try:
        df_list = load_list_data()
    except FileNotFoundError:
        st.error("一覧データが見つかりません。先にパイプラインを実行してください。")
        st.info("例: python -m src.cli pipeline --mode full ...")
        return
    except Exception:
        st.error("一覧データの読み込みに失敗しました。ファイル形式やパスを確認してください。")
        return

    if df_list.empty:
        st.warning("表示できる求人データがまだありません。")
        return

    render_hero(df_list)

    filtered = render_filters(df_list)

    st.markdown(
        f'<div class="section-title">求人一覧 <span class="muted">({len(filtered)}件)</span></div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.warning("条件に合う求人がありません。絞り込み条件を変えてみてください。")
        return

    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            clicked = render_job_card(row)
            if clicked:
                st.session_state.selected_url = row.get("url", "")
                st.switch_page("pages/1_求人詳細.py")


if __name__ == "__main__":
    main()