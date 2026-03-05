"""
STEAM Quiz Landing Page
Browse and select quizzes by grade and unit.
"""

import streamlit as st
from database import get_user, get_quiz_summary
from auth import require_auth, logout_button, is_authenticated
from config import (
    QUIZ_DATA, GRADE_NAMES, UNIT_NAMES, GRADE_EMOJIS,
    GRADE_COLORS, get_quizzes_by_grade, get_all_quizzes
)

# Page config
st.set_page_config(
    page_title="Quiz Central",
    page_icon="🎯",
    layout="wide"
)

require_auth()

# Sidebar
with st.sidebar:
    st.title("🎓 STEAM Quiz Central")
    st.markdown(f"👤 {st.session_state.full_name or st.session_state.user_name}")
    st.markdown("---")
    logout_button()

    # Navigation
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("📈 My Progress", use_container_width=True):
        st.switch_page("pages/4_Student_Progress.py")

# Custom CSS
st.markdown("""
<style>
    .quiz-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid;
        background: white;
    }
    .unit-header {
        padding: 15px 20px;
        border-radius: 8px;
        margin: 20px 0 15px 0;
        font-size: 1.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# State
if "selected_grade" not in st.session_state:
    st.session_state.selected_grade = "g1"

# Header
st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0;">🎯 Choose Your Quiz! 🎯</h1>
        <p style="margin: 5px 0 0 0;">Select a grade and pick a quiz to test your knowledge!</p>
    </div>
""", unsafe_allow_html=True)

# Grade tabs
grades = ["g1", "g2", "g3", "g4", "g5"]
col_width = len(grades)
cols = st.columns(col_width)

for i, grade in enumerate(grades):
    with cols[i]:
        active = st.session_state.selected_grade == grade
        color = GRADE_COLORS.get(grade, "#888")
        if st.button(
            f"{GRADE_EMOJIS.get(grade, '📚')} {GRADE_NAMES.get(grade, grade.upper())}",
            use_container_width=True,
            type="primary" if active else "secondary",
            key=f"grade_{grade}"
        ):
            st.session_state.selected_grade = grade
            st.rerun()

# Search
st.markdown("---")
search_query = st.text_input("🔍 Search quizzes...", placeholder="Search by keyword, title...")

# Get quizzes for selected grade
quizzes = get_quizzes_by_grade(st.session_state.selected_grade)

# Filter by search
if search_query:
    query = search_query.lower()
    quizzes = [
        q for q in quizzes
        if query in q["title"].lower() or
           query in q["description"].lower() or
           any(query in k.lower() for k in q["keywords"])
    ]

# Get user's quiz history
user = get_user(st.session_state.user_id)
completed_quizzes = {}
if user:
    from database import get_user_attempts
    attempts = get_user_attempts(user["id"])
    completed_quizzes = {a["quiz_id"]: a for a in attempts}

# Group by unit
unit3_quizzes = [q for q in quizzes if q["unit"] == "unit3"]
unit4_quizzes = [q for q in quizzes if q["unit"] == "unit4"]

# Display quizzes
if quizzes:
    for unit_num, unit_quizzes in [("unit3", unit3_quizzes), ("unit4", unit4_quizzes)]:
        if not unit_quizzes:
            continue

        # Unit header
        unit_bg = "#FFE0B2" if unit_num == "unit3" else "#C8E6C9"
        unit_border = "#FF9800" if unit_num == "unit3" else "#4CAF50"
        unit_emoji = "🎯" if unit_num == "unit3" else "⚡"

        st.markdown(f"""
            <div class="unit-header" style="background: {unit_bg}; border-left: 5px solid {unit_border}; color: #333;">
                {unit_emoji} {UNIT_NAMES.get(unit_num, unit_num)}
            </div>
        """, unsafe_allow_html=True)

        # Quiz cards
        for quiz in unit_quizzes:
            grade_color = GRADE_COLORS.get(quiz["grade"], "#888")

            # Check completion status
            status = ""
            if quiz["id"] in completed_quizzes:
                attempt = completed_quizzes[quiz["id"]]
                score_pct = (attempt["score"] / attempt["total_questions"]) * 100
                if score_pct >= 80:
                    status = "✅ "
                elif score_pct >= 60:
                    status = "📝 "
                else:
                    status = "🔄 "

            st.markdown(f"""
                <div class="quiz-card" style="border-left-color: {grade_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0 0 5px 0;">{status}{quiz['title']}</h3>
                            <p style="margin: 0; color: #666;">{quiz['chinese']}</p>
                            <p style="margin: 5px 0; font-size: 0.9rem;">{quiz['description']}</p>
                        </div>
                        <div style="text-align: right; min-width: 120px;">
                            <span style="background: {grade_color}20; padding: 5px 10px; border-radius: 15px; font-size: 0.85rem;">
                                📝 {quiz['questions']} questions
                            </span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"Start Quiz: {quiz['title']}", key=f"start_{quiz['id']}", use_container_width=True):
                    st.session_state.selected_quiz = quiz["id"]
                    st.switch_page("pages/2_Quiz_View.py")

            # Show best score if completed
            if quiz["id"] in completed_quizzes:
                summary = get_quiz_summary(st.session_state.user_id, quiz["id"])
                with col2:
                    st.metric("Best", f"{summary['best_score']}%")

else:
    st.markdown("### 🤔 No quizzes found")
    st.info("Try a different search term or select another grade.")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; color: #999;">
        <p>🌈 Spring 2026 STEAM Program | Happy Learning! 📚</p>
    </div>
""", unsafe_allow_html=True)
