import streamlit as st
from .auth import auth_ui, get_supabase_client, logout
from .publish_tab import render_publish_tab
from .headers import render_header
from .input_form import render_input_form
from .blog_tab import render_blog_tab
from .research_tab import render_research_tab
from .references_tab import render_references_tab

st.set_page_config(page_title="Research Blog Generator", page_icon="📝", layout="wide")


def main_app():
    render_header()

    st.session_state.setdefault("research_data", None)
    st.session_state.setdefault("blog_content", None)
    st.session_state.setdefault("active_tab", "input")
    st.session_state.setdefault("edited_blog", None)
    st.session_state.setdefault("image_path", None)
    st.session_state.setdefault("image_keyword", None)
    st.session_state.setdefault("image_version", 0)

    render_input_form()

    if st.session_state.research_data and st.session_state.blog_content:
        tab_cols = st.columns(5)
        tab_names = ["input", "blog", "research", "references", "publish"]
        tab_icons = ["📝", "📄", "🔬", "📚", "🚀"]

        for i, (tab_name, tab_icon) in enumerate(zip(tab_names, tab_icons)):
            with tab_cols[i]:
                if st.button(
                    f"{tab_icon} {tab_name.capitalize()}",
                    key=f"tab_{tab_name}",
                    use_container_width=True,
                ):
                    st.session_state.active_tab = tab_name

        st.markdown(
            f"""
        <style>
            button[data-testid="baseButton-secondary"][key="tab_{st.session_state.active_tab}"] {{
                background-color: #3498db !important;
                color: white !important;
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )

        if st.session_state.active_tab == "blog":
            render_blog_tab()
        elif st.session_state.active_tab == "research":
            render_research_tab()
        elif st.session_state.active_tab == "references":
            render_references_tab()
        elif st.session_state.active_tab == "publish":
            render_publish_tab()


# -------------------------
# Main Entry
# -------------------------
def run_app():
    if "user" not in st.session_state:
        auth_ui()
    else:
        st.sidebar.success(f"Logged in as {st.session_state['user'].user.email}")
        if st.sidebar.button("Logout"):
            logout()
        main_app()
