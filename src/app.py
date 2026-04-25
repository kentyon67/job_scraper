import pandas as pd
import streamlit as st

from src.analysis.ai.score import score_rows


CLASSIFIED_PATH = "data/output/jobs_classified.csv"


def load_classified_data() -> pd.DataFrame:
    return pd.read_csv(CLASSIFIED_PATH).fillna("")


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
            max-width: 1180px;
        }

        .hero-card {
            background: linear-gradient(135deg, #111827 0%, #1e293b 100%);
            border-radius: 26px;
            padding: 34px;
            margin-bottom: 24px;
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.22);
        }

        .hero-title {
            font-size: 3.1rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: -0.04em;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #e2e8f0;
            line-height: 1.9;
            max-width: 780px;
        }

        .profile-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 18px 20px;
            margin-bottom: 22px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }

        .profile-item {
            display: inline-block;
            background: #eef2ff;
            color: #1e3a8a;
            padding: 7px 12px;
            border-radius: 999px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.88rem;
            font-weight: 700;
        }

        .section-title {
            font-size: 1.28rem;
            font-weight: 900;
            color: #0f172a;
            margin-top: 10px;
            margin-bottom: 12px;
        }

        .job-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        }

        .rank-pill {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
            color: #111827;
            font-weight: 900;
            font-size: 0.95rem;
            padding: 7px 13px;
            border-radius: 999px;
            margin-bottom: 10px;
        }

        .job-title {
            font-size: 1.18rem;
            font-weight: 900;
            color: #111827;
            line-height: 1.45;
            margin-bottom: 6px;
        }

        .company {
            color: #475569;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .badge {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            margin-right: 6px;
            margin-bottom: 6px;
        }

        .badge-blue {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge-green {
            background: #dcfce7;
            color: #166534;
        }

        .badge-purple {
            background: #f3e8ff;
            color: #6b21a8;
        }

        .badge-orange {
            background: #ffedd5;
            color: #9a3412;
        }

        .muted {
            color: #475569;
            font-size: 0.93rem;
            line-height: 1.7;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            border-radius: 16px;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 900 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_profile_state() -> None:
    defaults = {
        "profile_set": False,
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


def build_user_profile_from_session_state() -> dict | None:
    if not st.session_state.get("profile_set", False):
        return None

    return {
        "preferred_languages": st.session_state.get("preferred_languages", []),
        "preferred_domains": st.session_state.get("preferred_domains", []),
        "prefer_global": st.session_state.get("prefer_global", False),
        "experience_level": st.session_state.get("experience_level", "Beginner"),
        "priority_mode": st.session_state.get("priority_mode", "Growth"),
        "preferred_locations": st.session_state.get("preferred_locations", []),
        "allow_remote": st.session_state.get("allow_remote", False),
    }


def rescore_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    profile = build_user_profile_from_session_state()
    rows = df.to_dict(orient="records")
    scored_rows = score_rows(rows, user_profile=profile)

    scored_df = pd.DataFrame(scored_rows).fillna("")

    for col in ["job_score", "fit_score", "total_score"]:
        scored_df[col] = pd.to_numeric(scored_df[col], errors="coerce").fillna(0)

    scored_df = scored_df.sort_values(
        by=["total_score", "fit_score", "job_score"],
        ascending=False,
    ).reset_index(drop=True)

    scored_df["rank"] = range(1, len(scored_df) + 1)
    return scored_df


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


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">JobFit</div>
            <div class="hero-subtitle">
                求人をAIで整理し、あなたの志向に合う仕事を見つけやすくする求人分析アプリです。<br>
                使用言語・職種・勤務形態・プロフィールとの相性をもとに、求人を比較できます。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("👤 プロフィール設定", use_container_width=True):
            st.switch_page("pages/profile_settings.py")


def render_profile_summary() -> None:
    if not st.session_state.get("profile_set", False):
        st.info("プロフィール未設定です。設定するとマッチ度が反映されます。")
        return

    items = []

    langs = st.session_state.get("preferred_languages", [])
    domains = st.session_state.get("preferred_domains", [])
    locs = st.session_state.get("preferred_locations", [])

    if langs:
        items.append(f"言語: {', '.join(langs)}")
    if domains:
        items.append(f"領域: {', '.join(normalize_category(d) for d in domains)}")
    if st.session_state.get("experience_level"):
        items.append(f"経験: {st.session_state.get('experience_level')}")
    if st.session_state.get("priority_mode"):
        items.append(f"重視: {st.session_state.get('priority_mode')}")
    if locs:
        items.append(f"勤務地: {', '.join(locs)}")
    if st.session_state.get("prefer_global", False):
        items.append("グローバル志向")
    if st.session_state.get("allow_remote", False):
        items.append("リモート許容")

    items_html = "".join(f'<span class="profile-item">{item}</span>' for item in items)

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="section-title">現在のプロフィール</div>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()

    with st.sidebar:
        st.markdown("### 検索・絞り込み")

        keyword = st.text_input("キーワード検索", "")

        categories = ["すべて"] + sorted(
            [x for x in filtered["job_category"].astype(str).unique() if x]
        )
        selected_category = st.selectbox(
            "職種カテゴリ",
            categories,
            format_func=lambda x: "すべて" if x == "すべて" else normalize_category(x),
        )

        work_styles = ["すべて"] + sorted(
            [x for x in filtered["work_style"].astype(str).unique() if x]
        )
        selected_work_style = st.selectbox("勤務スタイル", work_styles)

        employment_types = ["すべて"] + sorted(
            [x for x in filtered["employment_type"].astype(str).unique() if x]
        )
        selected_employment_type = st.selectbox("雇用形態", employment_types)

        language_keyword = st.text_input("使用言語 / 技術タグ", "")

        min_score = st.slider("最低総合スコア", 0, 200, 0, 10)

    if selected_category != "すべて":
        filtered = filtered[filtered["job_category"].astype(str) == selected_category]

    if selected_work_style != "すべて":
        filtered = filtered[filtered["work_style"].astype(str) == selected_work_style]

    if selected_employment_type != "すべて":
        filtered = filtered[filtered["employment_type"].astype(str) == selected_employment_type]

    if keyword:
        search_cols = [
            "title",
            "title_ja",
            "company_name",
            "ai_summary",
            "job_category",
            "work_style",
            "employment_type",
            "language_tags",
            "tech_keywords",
            "description_ja",
            "qualifications_ja",
        ]

        mask = False
        for col in search_cols:
            if col in filtered.columns:
                mask = mask | filtered[col].astype(str).str.contains(keyword, case=False, na=False)

        filtered = filtered[mask]

    if language_keyword:
        mask = (
            filtered["language_tags"].astype(str).str.contains(language_keyword, case=False, na=False)
            | filtered["tech_keywords"].astype(str).str.contains(language_keyword, case=False, na=False)
        )
        filtered = filtered[mask]

    filtered = filtered[
        pd.to_numeric(filtered["total_score"], errors="coerce").fillna(0) >= min_score
    ]

    return filtered


def render_job_card(row: pd.Series) -> None:
    rank = row.get("rank", "")
    title = row.get("title_ja", "") or row.get("title", "")
    company = row.get("company_name", "")
    total_score = int(row.get("total_score", 0))
    fit_score = int(row.get("fit_score", 0))
    job_score = int(row.get("job_score", 0))
    category = normalize_category(row.get("job_category", ""))
    work_style = row.get("work_style", "")
    employment_type = row.get("employment_type", "")
    language_tags = row.get("language_tags", "")
    ai_summary = str(row.get("ai_summary", "")).strip()

    with st.container(border=True):
        st.markdown(f'<span class="rank-pill">#{rank}</span>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="job-title">{title}</div>
            <div class="company">{company}</div>
            """,
            unsafe_allow_html=True,
        )

        badges = ""
        if category:
            badges += f'<span class="badge badge-blue">{category}</span>'
        if work_style:
            badges += f'<span class="badge badge-green">{work_style}</span>'
        if employment_type:
            badges += f'<span class="badge badge-orange">{employment_type}</span>'
        if str(row.get("ai_related", "")).lower() == "yes":
            badges += '<span class="badge badge-purple">AI関連</span>'

        st.markdown(badges, unsafe_allow_html=True)

        if language_tags:
            st.markdown(f'<div class="muted">{language_tags}</div>', unsafe_allow_html=True)

        if ai_summary:
            summary = ai_summary[:160] + "..." if len(ai_summary) > 160 else ai_summary
            st.markdown(
                f'<div class="muted" style="margin-top:10px;">{summary}</div>',
                unsafe_allow_html=True,
            )

        c1, c2, c3 = st.columns(3)
        c1.metric("総合", f"{total_score}/200")
        c2.metric("マッチ度", f"{fit_score}/100")
        c3.metric("求人価値", f"{job_score}/100")

        st.progress(min(max(total_score, 0), 200) / 200)

        btn_left, btn_center, btn_right = st.columns([1, 2, 1])
        with btn_center:
            if st.button(
                "詳細を見る",
                key=f"detail_{row.get('job_key', rank)}",
                use_container_width=True,
            ):
                st.session_state.selected_job_key = row.get("job_key", "")
                st.session_state.selected_url = row.get("url", "")
                st.switch_page("pages/job_detail.py")

def main() -> None:
    st.set_page_config(
        page_title="JobFit",
        page_icon="💼",
        layout="wide",
    )

    inject_css()
    init_profile_state()

    try:
        df_classified = load_classified_data()
    except FileNotFoundError:
        st.error("分類済みデータが見つかりません。pipeline を実行して jobs_classified.csv を作成してください。")
        return
    except Exception as e:
        st.error(f"分類済みデータの読み込みに失敗しました: {e}")
        return

    if df_classified.empty:
        st.warning("表示できる求人データがありません。")
        return

    df_scored = rescore_dataframe(df_classified)

    render_hero()
    render_profile_summary()

    filtered = render_filters(df_scored)

    st.markdown(
        f'<div class="section-title">求人一覧 <span style="color:#64748b;">({len(filtered)}件)</span></div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.warning("条件に合う求人がありません。絞り込み条件を変えてみてください。")
        return

    cols = st.columns(2)

    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            render_job_card(row)


if __name__ == "__main__":
    main()