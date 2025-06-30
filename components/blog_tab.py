import streamlit as st
import os
import json
from services import fetch_banner
from utils import image_to_base64


def render_blog_tab():
    st.subheader("Generated Blog")
    image_container = st.empty()

    if st.session_state.image_path and os.path.exists(st.session_state.image_path):
        image_container.markdown(
            f'<div class="banner-container">'
            f'<img src="data:image/png;base64,{image_to_base64(st.session_state.image_path)}" class="banner-image">'
            f'<div class="image-keyword">Image keyword: {st.session_state.image_keyword}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state.image_path:
        image_container.warning("Banner image not found at the specified path")
    else:
        image_container.warning("No banner image available")

    if st.button(
        "🖼️ Regenerate Image", use_container_width=True, key="regenerate_button"
    ):
        with st.spinner("Generating new image..."):
            try:
                new_image_path = fetch_banner(st.session_state.image_keyword)
                if new_image_path and os.path.exists(new_image_path):
                    st.session_state.image_path = new_image_path
                    image_container.markdown(
                        f'<div class="banner-container">'
                        f'<img src="data:image/png;base64,{image_to_base64(new_image_path)}" class="banner-image">'
                        f'<div class="image-keyword">Image keyword: {st.session_state.image_keyword}</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.success("Image regenerated successfully!")
                else:
                    st.error("Failed to generate new image")
            except Exception as e:
                st.error(f"Image regeneration failed: {str(e)}")

    col1, col2 = st.columns([2, 1])
    col1.metric("Research Duration", f"{st.session_state.duration:.2f} seconds")
    col2.metric("Image Keyword", st.session_state.image_keyword)

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        markdown_data = (
            st.session_state.blog_content
            if isinstance(st.session_state.blog_content, str)
            else json.dumps(st.session_state.blog_content, indent=2)
        )

        st.download_button(
            label="📥 Download Markdown",
            data=markdown_data,
            file_name="research_blog.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with btn_col2:
        st.download_button(
            label="📥 Download Research",
            data=json.dumps(st.session_state.research_data, indent=2),
            file_name="research_data.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("### Live Preview")
    st.markdown(st.session_state.edited_blog)

    if st.session_state.tags:
        st.markdown("### SEO Tags")
        tag_list = st.session_state.tags.split(",")
        st.markdown(
            " ".join(
                [
                    f"<span style='display:inline-block; background-color:#3498db; color:white; padding:0.3rem 0.6rem; margin:0.2rem; border-radius:20px; font-size:0.85rem;'>{t}</span>"
                    for t in tag_list
                ]
            ),
            unsafe_allow_html=True,
        )
