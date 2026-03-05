"""
Authentication module for STEAM Quiz Platform.
Handles login, logout, and session management.
"""

import streamlit as st
from database import authenticate_user, create_user, get_user, init_db, create_class


def init_auth():
    """Initialize authentication state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "full_name" not in st.session_state:
        st.session_state.full_name = None
    if "class_id" not in st.session_state:
        st.session_state.class_id = None


def login(username: str, password: str) -> bool:
    """Attempt to log in a user."""
    user = authenticate_user(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user_id = user["id"]
        st.session_state.user_role = user["role"]
        st.session_state.user_name = user["username"]
        st.session_state.full_name = user.get("full_name", "")
        st.session_state.class_id = user.get("class_id", "")
        return True
    return False


def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.full_name = None
    st.session_state.class_id = None
    st.rerun()


def is_authenticated() -> bool:
    """Check if a user is currently authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user_id() -> int:
    """Get the current user's ID."""
    return st.session_state.get("user_id")


def get_current_user_role() -> str:
    """Get the current user's role."""
    return st.session_state.get("user_role", "")


def get_current_user():
    """Get the current user's data."""
    if not is_authenticated():
        return None
    return get_user(get_current_user_id())


def is_teacher() -> bool:
    """Check if current user is a teacher."""
    return get_current_user_role() == "teacher"


def is_student() -> bool:
    """Check if current user is a student."""
    return get_current_user_role() == "student"


def require_auth():
    """Require authentication. Redirect to login if not authenticated."""
    if not is_authenticated():
        st.switch_page("app.py")


def require_teacher():
    """Require teacher role. Redirect if not a teacher."""
    require_auth()
    if not is_teacher():
        st.error("This page is only for teachers.")
        st.stop()


def show_login_page():
    """Display the login page."""
    st.set_page_config(page_title="STEAM Quiz Login", page_icon="🎓")

    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            color: #FF6B9D;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .login-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="login-title">🎓 STEAM Quiz Login</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Enter your credentials to continue</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "First Time Setup"])

        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    if login(username, password):
                        st.success(f"Welcome back, {st.session_state.full_name or username}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
                else:
                    st.warning("Please enter both username and password.")

        with tab2:
            st.info("👋 First time here? Please contact your teacher to create an account.")
            st.info("🔑 Teachers: Use the 'First Time Setup' tab to create your admin account.")

            admin_username = st.text_input("Admin Username", key="admin_username")
            admin_password = st.text_input("Admin Password", type="password", key="admin_password")
            admin_name = st.text_input("Full Name", key="admin_name")

            if st.button("Create Admin Account", use_container_width=True):
                if admin_username and admin_password and admin_name:
                    if create_user(admin_username, admin_password, "teacher", admin_name):
                        st.success("Admin account created! You can now log in.")
                    else:
                        st.error("Username already exists. Please choose another.")
                else:
                    st.warning("Please fill in all fields.")

        st.markdown("""
            <div style="text-align: center; margin-top: 30px; color: #999;">
                <p>🌈 Spring 2026 STEAM Program</p>
            </div>
        """, unsafe_allow_html=True)


def logout_button():
    """Display a logout button in the sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
