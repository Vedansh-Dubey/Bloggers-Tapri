import streamlit as st


def render_header():
    st.markdown(
        """
    <style>
        .header {
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
        }
        .card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .credibility-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .high-cred { background-color: #2ecc71; color: white; }
        .med-cred { background-color: #f39c12; color: white; }
        .low-cred { background-color: #e74c3c; color: white; }
        .user-cred { background-color: #3498db; color: white; }
        .reference-item {
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid #3498db;
            background-color: #f8f9fa;
            border-radius: 0 4px 4px 0;
        }
        .stTextArea textarea {
            min-height: 150px;
        }
        .banner-container {
            margin-bottom: 2rem;
            border-radius: 8px;
            overflow: hidden;
        }
        .banner-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
        }
        .image-keyword {
            font-size: 0.9rem;
            color: #666;
            text-align: center;
            margin-top: 0.5rem;
        }
        .tab-button-active {
            background-color: #3498db !important;
            color: white !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="header">'
        f"<h1>Research Blog Generator</h1>"
        f"<p>Generate comprehensive blogs using AI-powered agents</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
