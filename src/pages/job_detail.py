import pandas as pd
import streamlit as st


from src.analysis.ai.score import score_row



CLASSIFIED_PATH = "data/output/jobs_classified.csv"


def load_classified_data() -> pd.DataFrame:
    return pd.read_csv(CLASSIFIED_PATH).fillna("")


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
            max-width: 1050px;
        }

        .detail-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            padding: 28px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
            margin-bottom: 20px;
        }

        .detail-title {
            font-size: 2rem;
            font-weight: 900;
            color: #0f172a;
            line-height: 1.4;
            margin-bottom: 8px;
        }

        .muted {
            color: #475569;
            line-height: 1.8;
        }

        .info-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 18px;
            line-height: 1.9;
            color: #111827;
        }

        .badge {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 800;
            margin-right: 7px;
            margin-bottom: 7px;
            background: #eef2ff;
            color: #1e3a8a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="JobFit | 求人詳細",
        page_icon="💼",
        layout="wide",
    )

    inject_css()

    if st.button("← 一覧に戻る"):
        st.switch_page("app.py")

    selected_job_key = st.session_state.get("selected_job_key", "")
    selected_url = st.session_state.get("selected_url", "")

    if not selected_job_key and not selected_url:
        st.warning("詳細表示する求人が選ばれていません。一覧ページから選んでください。")
        return

    try:
        df = load_classified_data()
    except FileNotFoundError:
        st.error("jobs_classified.csv が見つかりません。pipeline を実行してください。")
        return
    except Exception as e:
        st.error(f"詳細データの読み込みに失敗しました: {e}")
        return

    matched = pd.DataFrame()

    if selected_job_key and "job_key" in df.columns:
        matched = df[df["job_key"].astype(str) == str(selected_job_key)]

    if matched.empty and selected_url:
        matched = df[df["url"].astype(str) == str(selected_url)]

    if matched.empty:
        st.error("選択した求人の詳細データが見つかりませんでした。")
        return

    base_row = matched.iloc[0].to_dict()
    profile = build_user_profile_from_session_state()
    row = score_row(base_row, user_profile=profile)

    title = row.get("title_ja", "") or row.get("title", "")
    company = row.get("company_name", "")
    total_score = int(float(row.get("total_score", 0) or 0))
    fit_score = int(float(row.get("fit_score", 0) or 0))
    job_score = int(float(row.get("job_score", 0) or 0))

    st.markdown(
        f"""
        <div class="detail-card">
            <div class="detail-title">{title}</div>
            <div class="muted">{company}</div>
            <div style="margin-top:14px;">
                <span class="badge">{normalize_category(row.get("job_category", ""))}</span>
                <span class="badge">{row.get("work_style", "")}</span>
                <span class="badge">{row.get("employment_type", "")}</span>
                <span class="badge">{row.get("language_tags", "")}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("総合スコア", f"{total_score}/200")
    c2.metric("マッチ度", f"{fit_score}/100")
    c3.metric("求人価値", f"{job_score}/100")

    st.progress(min(max(total_score, 0), 200) / 200)

    tab1, tab2, tab3, tab4 = st.tabs(["概要", "評価理由", "応募条件", "仕事内容"])

    with tab1:
        st.markdown("### AI要約")
        st.markdown(
            f'<div class="info-box">{row.get("ai_summary", "") or "AI要約はありません。"}</div>',
            unsafe_allow_html=True,
        )

        url = str(row.get("url", "")).strip()
        if url:
            st.link_button("求人ページを開く", url, use_container_width=True)

    with tab2:
        st.markdown("### 評価理由")
        st.markdown(
            f'<div class="info-box">{row.get("score_reason", "")}</div>',
            unsafe_allow_html=True,
        )

    with tab3:
        qualifications = row.get("qualifications_ja", "") or row.get("qualifications", "")
        st.markdown("### 応募条件")
        st.markdown(
            f'<div class="info-box">{qualifications or "応募条件の記載はありません。"}</div>',
            unsafe_allow_html=True,
        )

    with tab4:
        description = row.get("description_ja", "") or row.get("description", "")
        st.markdown("### 仕事内容")
        st.markdown(
            f'<div class="info-box">{description or "仕事内容の記載はありません。"}</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()