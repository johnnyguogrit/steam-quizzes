"""
STEAM Quiz Platform - Main Application
A Streamlit app for managing and taking STEAM quizzes.
"""

import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db
from auth import init_auth, login, is_authenticated, is_teacher, is_student, show_login_page, logout_button, get_current_user

# Initialize database
init_db()

# Initialize authentication state
init_auth()

# Page config
st.set_page_config(
    page_title="STEAM Quiz Central",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(135deg, #FF6B9D 0%, #C06C84 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .grade-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
    .g1 { background: #FFE0F0; color: #FF6B9D; }
    .g2 { background: #E8F5E9; color: #4CAF50; }
    .g3 { background: #F3E5F5; color: #9C27B0; }
    .g4 { background: #E3F2FD; color: #2196F3; }
    .g5 { background: #FFF3E0; color: #FF9800; }
</style>
""", unsafe_allow_html=True)


def show_main_app():
    """Display the main application after login."""
    # Sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 {st.session_state.full_name or st.session_state.user_name}")
        role_emoji = "👨‍🏫" if is_teacher() else "👨‍🎓"
        st.markdown(f"**{role_emoji} {st.session_state.user_role.capitalize()}**")
        if st.session_state.class_id:
            st.markdown(f"📚 Class: `{st.session_state.class_id}`")
        st.markdown("---")
        logout_button()

    # Main header
    st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0;">🎓 STEAM Quiz Central! 🎮</h1>
            <p style="margin: 5px 0 0 0;">Choose your grade and test your knowledge!</p>
        </div>
    """, unsafe_allow_html=True)

    # Role-based navigation
    if is_teacher():
        show_teacher_welcome()
    else:
        show_student_welcome()


def show_teacher_welcome():
    """Show welcome message for teachers."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/3_Teacher_Dashboard.py")

    with col2:
        if st.button("🎯 Browse Quizzes", use_container_width=True):
            st.switch_page("pages/1_Landing.py")

    with col3:
        if st.button("👥 Manage Classes", use_container_width=True):
            st.switch_page("pages/3_Teacher_Dashboard.py")

    st.markdown("---")

    # Quick stats
    user = get_current_user()
    from database import get_classes_by_teacher, get_class_statistics
    classes = get_classes_by_teacher(user["id"])

    if classes:
        st.subheader("📊 Your Classes")
        for cls in classes[:3]:
            stats = get_class_statistics(str(cls["id"]))
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(cls["name"], f"{stats['total_students']} students")
            with c2:
                st.metric("Total Attempts", stats["total_attempts"])
            with c3:
                st.metric("Avg Score", f"{stats['average_score']}%")
    else:
        st.info("👋 Welcome! Create your first class to get started.")
        if st.button("Create a Class", type="primary"):
            st.switch_page("pages/3_Teacher_Dashboard.py")


def show_student_welcome():
    """Show welcome message for students."""
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 Start a Quiz", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Landing.py")

    with col2:
        if st.button("📈 My Progress", use_container_width=True):
            st.switch_page("pages/4_Student_Progress.py")

    st.markdown("---")

    # Show recent activity
    from database import get_user_attempts, get_user_badges
    attempts = get_user_attempts(st.session_state.user_id)
    badges = get_user_badges(st.session_state.user_id)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Recent Quizzes")
        if attempts[:5]:
            for attempt in attempts[:5]:
                emoji = "⭐" if attempt["percentage"] >= 80 else "📝"
                st.markdown(f"{emoji} **{attempt['quiz_id'].upper()}** - {attempt['percentage']:.0f}%")
        else:
            st.info("No quizzes completed yet. Start your first quiz!")

    with col2:
        st.subheader("🏆 Your Badges")
        if badges:
            for badge in badges:
                st.markdown(f"{badge['badge_name']}")
        else:
            st.info("Complete quizzes to earn badges!")


# Main flow
if not is_authenticated():
    show_login_page()
else:
    show_main_app()
