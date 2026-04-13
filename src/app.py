import pandas as pd
import streamlit as st


LIST_PATH = "data/output/jobs_compared.csv"
DETAIL_PATH = "data/output/jobs_detail_view.csv"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_list = pd.read_csv(LIST_PATH)
    df_detail = pd.read_csv(DETAIL_PATH)

    # 欠損を空文字にそろえる
    df_list = df_list.fillna("")
    df_detail = df_detail.fillna("")

    return df_list, df_detail


def get_display_reason(row: pd.Series) -> str:
    short_reason = str(row.get("short_reason", "")).strip()
    score_reason = str(row.get("score_reason", "")).strip()

    if short_reason:
        return short_reason
    if score_reason:
        return score_reason
    return "理由なし"


def render_job_card(row: pd.Series) -> None:
    st.markdown(f"### {row.get('rank', '')}. {row.get('title', '')}")
    st.write(
        f"総合スコア: {row.get('total_score', '')} / "
        f"マッチ度: {row.get('fit_score', '')} / "
        f"求人価値: {row.get('job_score', '')}"
    )
    st.write(f"勤務地: {row.get('location', '')}")
    st.write(f"カテゴリ: {row.get('job_category', '')}")
    st.write(f"注目ポイント: {get_display_reason(row)}")


def render_detail(detail_row: pd.Series) -> None:
    st.markdown("---")
    st.subheader(detail_row.get("title", ""))

    st.write(f"勤務地: {detail_row.get('location', '')}")
    st.write(f"カテゴリ: {detail_row.get('job_category', '')}")
    st.write(
        f"総合スコア: {detail_row.get('total_score', '')} / "
        f"マッチ度: {detail_row.get('fit_score', '')} / "
        f"求人価値: {detail_row.get('job_score', '')}"
    )

    score_reason = str(detail_row.get("score_reason", "")).strip()
    ai_summary = str(detail_row.get("ai_summary", "")).strip()
    working_condition = str(detail_row.get("working_condition", "")).strip()
    qualifications = str(detail_row.get("qualifications", "")).strip()
    description = str(detail_row.get("description", "")).strip()
    url = str(detail_row.get("url", "")).strip()

    if score_reason:
        st.markdown("#### 評価理由")
        st.write(score_reason)

    if ai_summary:
        st.markdown("#### AI要約")
        st.write(ai_summary)

    if working_condition:
        with st.expander("勤務条件"):
            st.write(working_condition)

    if qualifications:
        with st.expander("応募条件"):
            st.write(qualifications)

    if description:
        with st.expander("仕事内容"):
            st.write(description)

    if url:
        st.link_button("求人ページを開く", url)


def main() -> None:
    st.set_page_config(page_title="求人おすすめ一覧", layout="wide")
    st.title("求人おすすめ一覧")

    df_list, df_detail = load_data()

    # サイドバーで簡易フィルタ
    st.sidebar.header("絞り込み")

    categories = ["すべて"] + sorted(
        [c for c in df_list["job_category"].astype(str).unique().tolist() if c]
    )
    selected_category = st.sidebar.selectbox("カテゴリ", categories)

    locations = ["すべて"] + sorted(
        [l for l in df_list["location"].astype(str).unique().tolist() if l]
    )
    selected_location = st.sidebar.selectbox("勤務地", locations)

    keyword = st.sidebar.text_input("タイトル検索")

    filtered = df_list.copy()

    if selected_category != "すべて":
        filtered = filtered[filtered["job_category"] == selected_category]

    if selected_location != "すべて":
        filtered = filtered[filtered["location"] == selected_location]

    if keyword.strip():
        filtered = filtered[
            filtered["title"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    st.write(f"表示件数: {len(filtered)}件")

    if filtered.empty:
        st.warning("条件に合う求人がありません。")
        return

    # 詳細表示対象のURLを選ぶ
    options = filtered.apply(
        lambda row: f"{row.get('rank', '')}. {row.get('title', '')}", axis=1
    ).tolist()
    option_to_url = {
        f"{row.get('rank', '')}. {row.get('title', '')}": row.get("url", "")
        for _, row in filtered.iterrows()
    }

    selected_option = st.selectbox("詳細を見る求人を選択", options)
    selected_url = option_to_url[selected_option]

    # 一覧表示
    st.markdown("## 一覧")
    for _, row in filtered.iterrows():
        with st.container(border=True):
            render_job_card(row)

    # 詳細表示
    matched_detail = df_detail[df_detail["url"] == selected_url]

    if matched_detail.empty:
        st.error("詳細データが見つかりませんでした。")
        return

    detail_row = matched_detail.iloc[0]

    st.markdown("## 詳細")
    render_detail(detail_row)


if __name__ == "__main__":
    main()