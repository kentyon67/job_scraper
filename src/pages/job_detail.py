import pandas as pd
import streamlit as st


DETAIL_PATH = "data/output/jobs_detail_view.csv"


def load_detail_data() -> pd.DataFrame:
    return pd.read_csv(DETAIL_PATH).fillna("")


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
            max-width: 1100px;
        }

        .detail-shell {
            background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 24px;
            margin-top: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.22);
        }

        .detail-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: white;
            margin-bottom: 10px;
            line-height: 1.4;
        }

        .metric-chip-wrap {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 12px 0 10px 0;
        }

        .metric-chip {
            background: rgba(255,255,255,0.08);
            color: #e5e7eb;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.9rem;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .reason-box {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 16px 18px;
            color: #111827;  
            line-height: 1.8;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 1rem;
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


def main() -> None:
    st.set_page_config(
        page_title="JobFit | 求人詳細",
        page_icon="💼",
        layout="wide",
    )

    inject_css()

    if st.button("← 一覧に戻る"):
        st.switch_page("app.py")

    selected_url = st.session_state.get("selected_url", "")

    if not selected_url:
        st.warning("詳細表示する求人が選ばれていません。一覧ページから選んでください。")
        if st.button("一覧ページへ"):
            st.switch_page("app.py")
        return

    try:
        df_detail = load_detail_data()
    except FileNotFoundError:
        st.error("詳細データが見つかりません。先にパイプラインを実行してください。")
        return
    except Exception:
        st.error("詳細データの読み込みに失敗しました。")
        return

    matched_detail = df_detail[df_detail["url"] == selected_url]

    if matched_detail.empty:
        st.error("選択した求人の詳細データが見つかりませんでした。")
        st.info("一覧ページに戻って別の求人を選んでください。")
        return

    detail_row = matched_detail.iloc[0]

    total_score = int(float(detail_row.get("total_score", 0) or 0))
    fit_score = int(float(detail_row.get("fit_score", 0) or 0))
    job_score = int(float(detail_row.get("job_score", 0) or 0))

    st.markdown(
        f"""
        <div class="detail-shell">
            <div class="detail-title">{detail_row.get('title_ja', '') or detail_row.get('title','')}</div>
            <div class="metric-chip-wrap">
                <div class="metric-chip">勤務地: {normalize_location(detail_row.get('location', ''))}</div>
                <div class="metric-chip">カテゴリ: {normalize_category(detail_row.get('job_category', ''))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("総合スコア", total_score)
    with c2:
        st.metric("マッチ度", fit_score)
    with c3:
        st.metric("求人価値", job_score)

    st.progress(total_score / 100)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["概要", "評価理由", "応募条件", "仕事内容"]
    )

    with tab1:
        ai_summary = str(detail_row.get("ai_summary", "")).strip()
        working_condition = str(detail_row.get("working_condition_ja", "") or detail_row.get("working_condition", "")).strip()

        if ai_summary:
            st.markdown("### AI要約")
            st.markdown(f'<div class="reason-box">{ai_summary}</div>', unsafe_allow_html=True)
        else:
            st.info("AI要約はありません。")

        if working_condition:
            st.markdown("### 勤務条件")
            st.markdown(f'<div class="reason-box">{working_condition}</div>', unsafe_allow_html=True)

        url = str(detail_row.get("url", "")).strip()
        if url:
            st.link_button("求人ページを開く", url, use_container_width=True)

    with tab2:
        score_reason = str(detail_row.get("score_reason", "")).strip()
        if score_reason:
            st.markdown("### 評価理由")
            st.markdown(f'<div class="reason-box">{score_reason}</div>', unsafe_allow_html=True)
        else:
            st.info("評価理由はありません。")

    with tab3:
        qualifications = str(detail_row.get("qualifications_ja","") or detail_row.get("qualifications", "")).strip()
        if qualifications:
            st.markdown("### 応募条件")
            st.markdown(f'<div class="reason-box">{qualifications}</div>', unsafe_allow_html=True)
        else:
            st.info("応募条件の記載はありません。")

    with tab4:
        description = str(detail_row.get("description_ja", "") or detail_row.get("description", "")).strip()
        if description:
            st.markdown("### 仕事内容")
            st.markdown(f'<div class="reason-box">{description}</div>', unsafe_allow_html=True)
        else:
            st.info("仕事内容の記載はありません。")


if __name__ == "__main__":
    main()