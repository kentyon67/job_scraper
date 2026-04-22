import streamlit as st


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
            max-width: 900px;
        }

        .page-title {
            font-size: 2.3rem;
            font-weight: 900;
            color: #0f172a;
            margin-bottom: 8px;
        }

        .page-subtitle {
            font-size: 1rem;
            color: #475569;
            line-height: 1.8;
            margin-bottom: 20px;
        }

        div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def save_profile_to_session_state(
    languages: list[str],
    domains: list[str],
    prefer_global: bool,
    experience_level: str,
    priority_mode: str,
    preferred_locations: list[str],
    allow_remote: bool,
) -> None:
    st.session_state["preferred_languages"] = languages
    st.session_state["preferred_domains"] = domains
    st.session_state["prefer_global"] = prefer_global
    st.session_state["experience_level"] = experience_level
    st.session_state["priority_mode"] = priority_mode
    st.session_state["preferred_locations"] = preferred_locations
    st.session_state["allow_remote"] = allow_remote


def main() -> None:
    st.set_page_config(
        page_title="JobFit | プロフィール設定",
        page_icon="👤",
        layout="wide",
    )

    inject_css()
    init_profile_state()

    top_left, top_right = st.columns([1.4, 6], vertical_alignment="center")

    with top_left:
        if st.button("← 一覧へ戻る", use_container_width=True):
            st.switch_page("app.py")

    with top_right:
        st.markdown(
            """
            <div class="page-title">プロフィール設定</div>
            <div class="page-subtitle">
                あなたの志向に合わせて、求人のおすすめ順や見え方を調整します。<br>
                保存後、一覧ページでスコアが再計算されます。
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.form("profile_form"):
        languages = st.multiselect(
            "希望言語",
            [
                "Python", "Java", "Go", "JavaScript", "TypeScript",
                "Scala", "SQL", "Kotlin", "Rust", "C++", "C#",
                "PHP", "Ruby"
            ],
            default=st.session_state.get("preferred_languages", ["Python"]),
        )

        domains = st.multiselect(
            "希望領域",
            [
                "Backend",
                "Data",
                "AI/ML",
                "Frontend",
                "Infra/SRE",
                "Security",
                "Mobile",
                "Product",
            ],
            default=st.session_state.get("preferred_domains", ["Backend", "Data"]),
            format_func=lambda x: {
                "Backend": "バックエンド",
                "Data": "データ",
                "AI/ML": "AI・機械学習",
                "Frontend": "フロントエンド",
                "Infra/SRE": "インフラ / SRE",
                "Security": "セキュリティ",
                "Mobile": "モバイル",
                "Product": "プロダクト",
            }.get(x, x),
        )

        toggle_col1, toggle_col2 = st.columns(2)

        with toggle_col1:
            prefer_global = st.toggle(
                "グローバル環境を重視する",
                value=st.session_state.get("prefer_global", True),
            )

        with toggle_col2:
            allow_remote = st.toggle(
                "リモート勤務を許容する",
                value=st.session_state.get("allow_remote", True),
            )

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            experience_level = st.selectbox(
                "経験レベル",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(
                    st.session_state.get("experience_level", "Beginner")
                ),
                format_func=lambda x: {
                    "Beginner": "初学者",
                    "Intermediate": "中級",
                    "Advanced": "上級",
                }.get(x, x),
            )

        with info_col2:
            priority_mode = st.selectbox(
                "重視モード",
                ["Growth", "Balanced", "Realistic"],
                index=["Growth", "Balanced", "Realistic"].index(
                    st.session_state.get("priority_mode", "Growth")
                ),
                format_func=lambda x: {
                    "Growth": "成長重視",
                    "Balanced": "バランス重視",
                    "Realistic": "現実性重視",
                }.get(x, x),
            )

        preferred_locations = st.multiselect(
            "希望勤務地",
            [
                "Tokyo",
                "Osaka",
                "Kyoto",
                "Hokkaido",
                "Fukuoka",
                "Nagoya",
                "Remote",
                "Japan",
            ],
            default=st.session_state.get("preferred_locations", ["Tokyo"]),
        )

        submit = st.form_submit_button("保存して一覧に反映", use_container_width=True)

    if submit:
        save_profile_to_session_state(
            languages=languages,
            domains=domains,
            prefer_global=prefer_global,
            experience_level=experience_level,
            priority_mode=priority_mode,
            preferred_locations=preferred_locations,
            allow_remote=allow_remote,
        )

        st.success("プロフィールを保存しました。一覧ページでスコアに反映されます。")

        try:
            st.switch_page("app.py")
        except Exception:
            st.info("一覧ページへ戻って反映を確認してください。")


if __name__ == "__main__":
    main()