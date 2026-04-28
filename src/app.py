import pandas as pd
import streamlit as st

try:
    from src.analysis.ai.score import score_rows
except ModuleNotFoundError:
    from analysis.ai.score import score_rows


CLASSIFIED_PATH = "data/output/jobs_classified.csv"


# =========================
# CSS（UI）
# =========================
def inject_css():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display:none;}
    [data-testid="collapsedControl"] {display:none;}

    .job-card {
        border:1px solid #e2e8f0;
        border-radius:18px;
        padding:18px;
        margin-bottom:14px;
        background:#ffffff;
        box-shadow:0 6px 18px rgba(0,0,0,0.05);
    }

    .title {
        font-size:18px;
        font-weight:700;
        color:#111;
    }

    .company {
        color:#666;
        font-size:14px;
        margin-bottom:8px;
    }

    .badge {
        display:inline-block;
        padding:4px 10px;
        border-radius:999px;
        font-size:12px;
        margin-right:5px;
        margin-top:5px;
        background:#eef2ff;
    }
    </style>
    """, unsafe_allow_html=True)


# =========================
# 日本語変換
# =========================
def jp_work(x):
    return {
        "Remote":"リモート",
        "Hybrid":"ハイブリッド",
        "Onsite":"出社"
    }.get(x, x)

def jp_emp(x):
    return {
        "Internship":"インターン",
        "FullTime":"正社員",
        "Contract":"契約",
        "PartTime":"アルバイト"
    }.get(x, x)

def jp_cat(x):
    return {
        "Backend":"バックエンド",
        "Frontend":"フロントエンド",
        "Data":"データ",
        "AI/ML":"AI",
    }.get(x, x)


# =========================
# プロフィール
# =========================
def build_profile():
    if not st.session_state.get("profile_set"):
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


# =========================
# データ
# =========================
def load_data():
    return pd.read_csv(CLASSIFIED_PATH).fillna("")


# =========================
# スコア
# =========================
def rescore(df):
    rows = df.to_dict("records")
    scored = score_rows(rows, user_profile=build_profile())
    df = pd.DataFrame(scored)

    df["total_score"] = pd.to_numeric(df["total_score"])
    df["fit_score"] = pd.to_numeric(df["fit_score"])
    df["job_score"] = pd.to_numeric(df["job_score"])

    df = df.sort_values("total_score", ascending=False)
    df["rank"] = range(1, len(df)+1)
    return df


# =========================
# 検索（メインUI）
# =========================
def filter_ui(df):
    st.subheader("検索・絞り込み")

    keyword = st.text_input("キーワード")

    col1,col2,col3 = st.columns(3)

    with col1:
        cat = st.selectbox("職種", ["すべて"] + list(df["job_category"].unique()))

    with col2:
        work = st.selectbox("勤務形態", ["すべて"] + list(df["work_style"].unique()))

    with col3:
        emp = st.selectbox("雇用形態", ["すべて"] + list(df["employment_type"].unique()))

    if keyword:
        df = df[df["title"].str.contains(keyword, case=False, na=False)
                | df["title_ja"].str.contains(keyword, case=False, na=False)]

    if cat != "すべて":
        df = df[df["job_category"] == cat]

    if work != "すべて":
        df = df[df["work_style"] == work]

    if emp != "すべて":
        df = df[df["employment_type"] == emp]

    return df


# =========================
# カード
# =========================
def render_card(row):
    st.markdown('<div class="job-card">', unsafe_allow_html=True)

    title = row["title_ja"] or row["title"]

    st.markdown(f'<div class="title">#{row["rank"]} {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="company">{row["company_name"]}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="badge">{jp_cat(row["job_category"])}</span>
    <span class="badge">{jp_work(row["work_style"])}</span>
    <span class="badge">{jp_emp(row["employment_type"])}</span>
    """, unsafe_allow_html=True)

    st.write(row["ai_summary"][:120]+"...")

    c1,c2,c3 = st.columns(3)
    c1.metric("総合", int(row["total_score"]))
    c2.metric("マッチ", int(row["fit_score"]))
    c3.metric("価値", int(row["job_score"]))

    colL,colC,colR = st.columns([1,2,1])
    with colC:
        if st.button("詳細", key=row["job_key"], use_container_width=True):
            st.session_state.selected_job_key = row["job_key"]
            st.switch_page("pages/job_detail.py")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# main
# =========================
def main():
    st.set_page_config(layout="wide")

    inject_css()

    st.title("JobFit")

    if st.button("プロフィール設定"):
        st.switch_page("pages/profile_settings.py")

    df = load_data()
    df = rescore(df)
    df = filter_ui(df)

    for _,row in df.iterrows():
        render_card(row)


if __name__ == "__main__":
    main()