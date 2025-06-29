import streamlit as st
import re
from utils.helpers import parse_references, get_credibility_badge

def render_references_tab():
    st.subheader("Research References")
    references = parse_references(st.session_state.blog_content)
    
    if references:
        for ref_id, content in references.items():
            url_match = re.search(r"https?://[^\s\]]+", content)
            source_url = url_match.group(0) if url_match else "User Provided"
            
            clean_content = re.sub(r"https?://[^\s\]]+", "", content).strip()
            
            source_credibility = "Medium"
            if "User Provided" in content:
                source_credibility = "User Provided"
            elif any(d in source_url for d in ['.edu', '.gov', 'academic', 'research']):
                source_credibility = "High"
            elif any(d in source_url for d in ['blog', 'medium.com', 'wordpress']):
                source_credibility = "Low"
            
            st.markdown(
                f"<div class='reference-item'>"
                f"<strong>[{ref_id}] {clean_content}</strong><br>"
                f"<div><strong>URL:</strong> <a href='{source_url}' target='_blank'>{source_url}</a></div>"
                f"<div><strong>Credibility:</strong> {get_credibility_badge(source_credibility)}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No references found in the blog content")