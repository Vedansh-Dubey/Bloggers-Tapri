import streamlit as st
import os
from utils.helpers import clean_tag
from services.devto_api import publish_to_devto

def render_publish_tab():
    st.subheader("Publishing Options")
    
    api_key_input = st.text_input(
        "DEV.to API Key (required for publishing)",
        type="password",
        help="Your API key will only be used for this publish action and won't be stored anywhere"
    )
    st.write("")

    st.markdown(
        """
        <small style="color: gray;">
        🔒 Your API key is used only for this publish action and is never stored or logged. 
        Get your API key from <a href="https://dev.to/settings/account" target="_blank">DEV.to settings</a>.
        </small>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Publish as Draft", use_container_width=True):
            publish_blog(api_key_input, published=False)
    with col2:
        if st.button("🌍 Publish Live", use_container_width=True):
            publish_blog(api_key_input, published=True)

def publish_blog(api_key: str, published: bool = False):
    if not api_key:
        if published:
            st.error("API key is required for publishing")
            return
        else:
            api_key = os.getenv("DEV_TO_API_KEY") # type: ignore            
    
    with st.spinner("Publishing to Dev.to..."):            
        original_tags = st.session_state.tags.split(",")
        cleaned_tags = [clean_tag(tag.strip()) for tag in original_tags][:4] 
        
        try:
            response = publish_to_devto(
                api_key=api_key,
                title=st.session_state.research_data.get("topic", "AI Blog"),
                content=st.session_state.edited_blog,
                image_path=st.session_state.image_path,
                published=published,
                tags=",".join(cleaned_tags)
            )
            status = "published" if published else "saved as draft"
            st.success(f"✅ Blog {status}: [View Post](https://dev.to{response['path']})")
        except Exception as e:
            st.error(f"❌ Failed to publish blog: {e}")