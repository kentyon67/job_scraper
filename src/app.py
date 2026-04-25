import pandas as pd
import streamlit as st
from src.analysis.ai.score import score_rows

CLASSIFIED_PATH = "data/output/jobs_classified.csv"


def load_classified_data():
    return pd.read_csv(CLASSIFIED_PATH).fillna("")


def build_user_profile():
    if "profile_set" not in st.sesseion_state :
        return None

    return {
        "preferred_languages": st.session_state.get("preferred_languages", ["Python"]),
        "preferred_domains": st.session_state.get("preferred_domains", ["Backend"]),
        "prefer_global": st.session_state.get("prefer_global", True),
        "experience_level": st.session_state.get("experience_level", "Beginner"),
        "priority_mode": st.session_state.get("priority_mode", "Growth"),
        "preferred_locations": st.session_state.get("preferred_locations", ["Tokyo"]),
        "allow_remote": st.session_state.get("allow_remote", True),
    }



def filter_dataframe(df):
    keyword = st.text_input("キーワード検索")

    if keyword:
        df = df[
            df["title"].str.contains(keyword, case=False, na=False)
            | df["title_ja"].str.contains(keyword, case=False, na=False)
            | df["ai_summary"].str.contains(keyword, case=False, na=False)
            ]

    return df


def rescore(df):
    profile = build_user_profile()
    rows = df.to_dict("records")
    scored = score_rows(rows, user_profile=profile)
    df = pd.DataFrame(scored)

    for col in ["job_score", "fit_score", "total_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values("total_score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df



def render_card(row):
    title = row.get("title_ja") or row.get("title")
    company = row.get("company_name", "")
    summary = row.get("ai_summary", "")[:120]

    st.markdown(f"### #{row['rank']} {title}")
    st.caption(company)

    badges = []
    if row.get("work_style") == "Remote":
        badges.append("🟢 リモート")
    if row.get("global_related") == "Yes":
        badges.append("🌍 グローバル")
    if row.get("ai_related") == "Yes":
        badges.append("🤖 AI")

    st.write(" ".join(badges))

    st.write(summary + "...")

    c1, c2, c3 = st.columns(3)
    c1.metric("総合", int(row["total_score"]))
    c2.metric("マッチ", int(row["fit_score"]))
    c3.metric("価値", int(row["job_score"]))

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("詳細", key=row["job_key"], use_container_width=True):
            st.session_state.selected_job_key = row["job_key"]
            st.switch_page("pages/job_detail.py")


def main():
    st.title("JobFit")

    df = load_classified_data()

    filtered = filter_dataframe(df)

    scored = rescore(filtered)

    if st.button("⚙️ プロフィール設定"):
        st.switch_page("pages/profile_settings.py")

    st.write(f"{len(scored)} 件")

    for _, row in scored.iterrows():
        render_card(row)
        st.divider()


if __name__ == "__main__":
    main()