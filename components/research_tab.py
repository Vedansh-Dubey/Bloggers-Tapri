import streamlit as st
from utils.helpers import get_credibility_badge

def render_research_tab():
    st.subheader("Research Data")
    
    if "key_findings" in st.session_state.research_data:
        st.write(f"**Topic**: {st.session_state.research_data.get('topic', '')}")
        
        if "sources" in st.session_state.research_data:
            st.write(f"**Sources**: User: {st.session_state.research_data['sources']['user']}, "
                    f"Auto: {st.session_state.research_data['sources']['auto']}")
        else:
            st.write("**Sources**: Not available")
        
        st.subheader("Key Findings")
        for finding in st.session_state.research_data["key_findings"]:
            with st.container():
                st.markdown(
                    f"<div class='card'>"
                    f"<h4>{finding['fact']}</h4>"
                    f"<p>{finding.get('supporting_evidence', 'No evidence provided')}</p>"
                    f"<div><strong>Source:</strong> <a href='{finding.get('source_url', '#')}' target='_blank'>{finding.get('source_url', 'No URL')}</a></div>"
                    f"<div><strong>Credibility:</strong> {get_credibility_badge(finding.get('source_credibility', 'Medium'))}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    
    if "summary" in st.session_state.research_data:
        with st.expander("Research Summary"):
            st.markdown(st.session_state.research_data["summary"])