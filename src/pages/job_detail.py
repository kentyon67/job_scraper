import pandas as pd
import streamlit as st
from src.analysis.ai.score import score_row

PATH = "data/output/jobs_classified.csv"


def load():
    return pd.read_csv(PATH).fillna("")


def build_profile():
    return {
        "preferred_languages": st.session_state.get("preferred_languages", ["Python"]),
        "preferred_domains": st.session_state.get("preferred_domains", ["Backend"]),
        "prefer_global": st.session_state.get("prefer_global", True),
        "experience_level": st.session_state.get("experience_level", "Beginner"),
        "priority_mode": st.session_state.get("priority_mode", "Growth"),
        "preferred_locations": st.session_state.get("preferred_locations", ["Tokyo"]),
        "allow_remote": st.session_state.get("allow_remote", True),
    }


def main():
    st.title("求人詳細")

    key = st.session_state.get("selected_job_key")

    df = load()
    row = df[df["job_key"] == key]

    if row.empty:
        st.error("見つからない")
        return

    row = row.iloc[0].to_dict()

    # 🔥 ここで再スコア
    scored = score_row(row, user_profile=build_profile())

    st.header(scored.get("title_ja") or scored.get("title"))
    st.caption(scored.get("company_name"))

    st.metric("総合スコア", int(scored["total_score"]))
    st.metric("マッチ度", int(scored["fit_score"]))

    st.write("### AI要約")
    st.write(scored.get("ai_summary"))

    st.write("### 仕事内容")
    st.write(scored.get("description_ja") or scored.get("description"))

    st.write("### 応募条件")
    st.write(scored.get("qualifications_ja") or scored.get("qualifications"))

    st.write("### 評価理由")
    st.write(scored.get("score_reason"))

    if st.button("戻る"):
        st.switch_page("app.py")


if __name__ == "__main__":
    main()