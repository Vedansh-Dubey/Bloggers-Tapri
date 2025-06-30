# auth.py
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv


def auth_ui():
    st.title("🔐 Login or Sign Up")

    mode = st.radio("Select mode", ["Login", "Sign Up"], horizontal=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Continue"):
        supabase = get_supabase_client()
        try:
            if mode == "Login":
                user = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state["user"] = user
                st.success("Login successful!")
                st.rerun()
            else:
                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {
                            "email_redirect_to": "https://bloggers-tapri.streamlit.app"
                        },
                    }
                )
                st.success(
                    "Signup successful! Please check your email to verify your account."
                )
                
        except Exception as e:
            st.error(f"{mode} failed: {e}")

    st.stop()


@st.cache_resource
def get_supabase_client() -> Client:
    SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials not configured!")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def show_auth_form():
    """Show login/signup form and handle authentication"""
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login", key="login_btn"):
            handle_login(email, password)

    with tab2:
        st.subheader("Create Account")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Sign Up", key="signup_btn"):
            handle_signup(email, password)


def handle_login(email: str, password: str):
    if not email or not password:
        st.error("Please enter both email and password")
        return

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        user = supabase.auth.get_user()
        if not user.user.email_confirmed_at:  # type: ignore
            st.error(
                "Please verify your email before logging in. Check your inbox for the verification link."
            )
            logout()
            return

        st.session_state.user = response
        st.success("Login successful!")
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {str(e)}")


def handle_signup(email: str, password: str):
    if not email or not password:
        st.error("Please enter both email and password")
        return

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": "https://bloggers-tapri.streamlit.app"
                },
            }
        )

        st.success(
            """
        Signup successful! 
        Please check your email to verify your account.
        You'll be able to login after verification.
        """
        )

        if "user" in st.session_state:
            del st.session_state.user

    except Exception as e:
        st.error(f"Signup failed: {str(e)}")


def logout():
    if "user" in st.session_state:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        del st.session_state.user
    st.rerun()


def check_authenticated():
    """Check if user is authenticated and email is verified"""
    supabase = get_supabase_client()

    if "user" not in st.session_state:
        show_auth_form()
        st.stop()

    try:
        user = supabase.auth.get_user()
        if not user.user.email_confirmed_at:  # type: ignore
            st.error(
                "Please verify your email before accessing the app. Check your inbox."
            )
            logout()
            st.stop()
    except Exception as e:
        st.error(f"Authentication check failed: {str(e)}")
        logout()
        st.stop()
