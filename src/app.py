import pandas as pd
import streamlit as st


LIST_PATH = "data/output/jobs_compared.csv"


def load_list_data() -> pd.DataFrame:
    return pd.read_csv(LIST_PATH).fillna("")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: #f8fafc;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 32px;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        }

        .hero-title {
            font-size: 3.2rem;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 12px;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            font-size: 1.12rem;
            color: #e2e8f0;
            line-height: 1.9;
            margin-bottom: 14px;
            max-width: 760px;
        }

        .metric-chip-wrap {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .metric-chip {
            background: rgba(255,255,255,0.10);
            color: #f8fafc;
            padding: 8px 13px;
            border-radius: 999px;
            font-size: 0.92rem;
            border: 1px solid rgba(255,255,255,0.08);
            font-weight: 700;
        }

        .profile-summary-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 18px 20px;
            margin-bottom: 26px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        .profile-summary-header {
            font-size: 1.05rem;
            font-weight: 900;
            color: #0f172a;
            margin-bottom: 14px;
        }

        .profile-item {
            display: inline-block;
            background: #eef2ff;
            color: #1e3a8a;
            padding: 8px 12px;
            border-radius: 999px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.9rem;
            font-weight: 700;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 900;
            color: #0f172a;
            margin-top: 8px;
            margin-bottom: 12px;
        }

        .rank-pill {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
            color: #111827;
            font-weight: 900;
            font-size: 1rem;
            padding: 8px 14px;
            border-radius: 999px;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 800;
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .badge-category {
            background: #2563eb;
            color: #ffffff;
        }

        .badge-location {
            background: #10b981;
            color: #052e16;
        }

        .card-title {
            font-size: 1.12rem;
            font-weight: 900;
            color: #111827;
            margin-top: 4px;
            margin-bottom: 10px;
            line-height: 1.5;
        }

        .muted {
            color: #475569;
            font-size: 0.94rem;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            border-radius: 16px;
        }

        div[data-testid="stMetricLabel"] {
            color: #475569 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 900 !important;
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


def init_profile_state() -> None:
    defaults = {
        "preferred_languages": ["Python"],
        "preferred_domains": ["Backend", "Data"],
        "prefer_global": True,
        "experience_level": "Beginner",
        "priority_mode": "Growth",
        "preferred_locations": ["Tokyo"],
        "allow_remote": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">JobFit</div>
            <div class="hero-subtitle">
                求人をAIで整理して、あなたに合いそうな仕事を見つけやすくするアプリです。<br>
                カード一覧で比較して、気になる求人だけ詳しく確認できます。
            </div>
            <div class="metric-chip-wrap">
                <div class="metric-chip">AI要約つき</div>
                <div class="metric-chip">一覧 + 詳細ページ対応</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile_summary() -> None:
    preferred_languages = st.session_state.get("preferred_languages", [])
    preferred_domains = st.session_state.get("preferred_domains", [])
    prefer_global = st.session_state.get("prefer_global", False)
    experience_level = st.session_state.get("experience_level", "")
    priority_mode = st.session_state.get("priority_mode", "")
    preferred_locations = st.session_state.get("preferred_locations", [])
    allow_remote = st.session_state.get("allow_remote", False)

    items = []

    if preferred_languages:
        items.append(f"言語: {', '.join(preferred_languages)}")
    if preferred_domains:
        items.append(f"領域: {', '.join(normalize_category(d) for d in preferred_domains)}")
    if experience_level:
        items.append(f"経験: {experience_level}")
    if priority_mode:
        items.append(f"重視: {priority_mode}")
    if preferred_locations:
        items.append(f"勤務地: {', '.join(preferred_locations)}")
    if prefer_global:
        items.append("グローバル志向")
    if allow_remote:
        items.append("リモート許容")

    # ボタンを左に置く
    nav_col1, nav_col2 = st.columns([1.4, 6], vertical_alignment="center")

    with nav_col1:
        if st.button("👤\nプロフィール", key="profile_summary_button", use_container_width=True):
            try:
                st.switch_page("pages/profile_settings.py")
            except Exception:
                st.error("プロフィール設定ページへ移動できませんでした。")

    with nav_col2:
        st.markdown(
            '<div class="section-title">現在のプロフィール設定</div>',
            unsafe_allow_html=True,
        )

    items_html = "".join(
        [f'<span class="profile-item">{item}</span>' for item in items]
    )

    st.markdown(
        f"""
        <div class="profile-summary-card">
            {items_html}
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
                <div class="card-title">{row.get('title_ja', '') or row.get('title', '')}</div>
                <div class="muted">注目ポイント: {row.get('short_reason', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("総合", total_score)
        with c2:
            st.metric("マッチ度", fit_score)
        with c3:
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
    init_profile_state()

    try:
        df_list = load_list_data()
    except FileNotFoundError:
        st.error("一覧データが見つかりません。先にパイプラインを実行してください。")
        return
    except Exception:
        st.error("一覧データの読み込みに失敗しました。")
        return

    if df_list.empty:
        st.warning("表示できる求人データがまだありません。")
        return

    render_hero()
    render_profile_summary()

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
                try:
                    st.switch_page("pages/job_detail.py")
                except Exception:
                    st.error("詳細ページへ移動できませんでした。")


if __name__ == "__main__":
    main()