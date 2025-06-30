import streamlit as st
from services import agno_service
from services.unsplash import fetch_banner
from utils import logger as st_logger
from datetime import datetime
from utils.helpers import calculate_duration
from agents import BlogWriter

def render_input_form():
    with st.form("research_form"):
        st.subheader("Research Parameters")
        
        col1, col2 = st.columns([3, 1])
        topic = col1.text_input(
            "Research Topic*",
            value="AI-Powered Cybersecurity Systems: Attack Prediction Models",
            help="Enter the main topic for your research"
        )
        
        user_research = st.text_area(
            "Your Research Notes (Optional)",
            height=200,
            help="Add any existing research notes you want to include"
        )
        
        submitted = st.form_submit_button("Generate Blog")
        
        if submitted:
            if not topic:
                st.error("Please enter a research topic")
                st.stop()
                
            with st.spinner("🔍 Conducting research and generating blog..."):
                try:
                    start_time = datetime.now()
                    image_keyword, research_data, blog, tags = agno_service.run_agno_services(topic, user_research)
                    image_path = fetch_banner(image_keyword)
                    
                    duration = calculate_duration(start_time)
                    st_logger.info(f"Research completed in {duration:.2f} seconds")
                    
                    writer = BlogWriter()
                    cleaned_blog = writer._convert_escaped_newlines(blog["final"]) # type: ignore
                    # cleaned_blog = blog
                    
                    st.session_state.research_data = research_data
                    st.session_state.blog_content = cleaned_blog
                    st.session_state.edited_blog = cleaned_blog
                    st.session_state.image_keyword = image_keyword
                    st.session_state.image_path = image_path
                    st.session_state.duration = duration
                    st.session_state.active_tab = "blog"
                    st.session_state.tags = tags
                    
                except Exception as e:
                    st_logger.error(f"Research failed: {str(e)}")
                    st.error(f"Research failed: {str(e)}")