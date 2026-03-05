"""
Student Progress Page
View personal quiz history, badges, and achievements.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_user_attempts, get_user_badges, get_quiz_summary
from auth import require_auth, logout_button
from config import QUIZ_DATA, GRADE_NAMES, GRADE_EMOJIS, get_all_quizzes

# Page config
st.set_page_config(
    page_title="My Progress",
    page_icon="📈",
    layout="wide"
)

require_auth()

# Sidebar
with st.sidebar:
    st.title("📈 My Progress")
    st.markdown(f"👤 {st.session_state.full_name or st.session_state.user_name}")
    st.markdown("---")
    logout_button()

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🎯 Browse Quizzes", use_container_width=True):
        st.switch_page("pages/1_Landing.py")

# Custom CSS
st.markdown("""
<style>
    .badge {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
    }
    .stat-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .progress-item {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        background: white;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0;">📈 My Progress</h1>
        <p style="margin: 5px 0 0 0;">Track your learning journey and achievements!</p>
    </div>
""", unsafe_allow_html=True)

# Get user data
user_id = st.session_state.user_id
attempts = get_user_attempts(user_id)
badges = get_user_badges(user_id)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Statistics", "🏆 Badges", "📝 History"])

with tab1:
    st.header("📊 My Statistics")

    if attempts:
        # Calculate stats
        total_quizzes = len(set(a["quiz_id"] for a in attempts))
        total_attempts = len(attempts)
        scores = [a["score"] / a["total_questions"] for a in attempts if a["total_questions"] > 0]
        avg_score = sum(scores) / len(scores) * 100 if scores else 0
        best_score = max(scores) * 100 if scores else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Unique Quizzes", total_quizzes)
        with col2:
            st.metric("Total Attempts", total_attempts)
        with col3:
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col4:
            st.metric("Best Score", f"{best_score:.1f}%")

        # Progress by grade
        st.subheader("Progress by Grade")

        all_quizzes = get_all_quizzes()
        quizzes_by_grade = {}
        for quiz in all_quizzes:
            grade = quiz["grade"]
            if grade not in quizzes_by_grade:
                quizzes_by_grade[grade] = []
            quizzes_by_grade[grade].append(quiz)

        for grade in ["g1", "g2", "g3", "g4", "g5"]:
            if grade not in quizzes_by_grade:
                continue

            total_in_grade = len(quizzes_by_grade[grade])
            completed_in_grade = len(set(
                a["quiz_id"] for a in attempts
                if a["quiz_id"].startswith(grade)
            ))

            if completed_in_grade > 0:
                progress_pct = completed_in_grade / total_in_grade
                grade_name = GRADE_NAMES.get(grade, grade.upper())
                grade_emoji = GRADE_EMOJIS.get(grade, "📚")

                st.markdown(f"**{grade_emoji} {grade_name}**")
                st.progress(progress_pct)
                st.markdown(f"{completed_in_grade}/{total_in_grade} quizzes completed\n")

        # Performance by quiz
        st.subheader("Quiz Performance")

        quiz_summaries = {}
        for quiz in all_quizzes:
            summary = get_quiz_summary(user_id, quiz["id"])
            if summary["attempts"] > 0:
                quiz_summaries[quiz["id"]] = {
                    "title": quiz["title"],
                    "grade": quiz["grade"].upper(),
                    "attempts": summary["attempts"],
                    "best_score": summary["best_score"],
                    "avg_score": summary["avg_score"]
                }

        if quiz_summaries:
            df_data = []
            for quiz_id, data in sorted(quiz_summaries.items()):
                df_data.append({
                    "Quiz": data["title"],
                    "Grade": data["grade"],
                    "Attempts": data["attempts"],
                    "Best Score": f"{data['best_score']}%",
                    "Avg Score": f"{data['avg_score']}%"
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No quiz attempts yet. Complete your first quiz!")

    else:
        st.markdown("### 👋 Welcome to your progress page!")
        st.info("You haven't completed any quizzes yet. Start your first quiz to track your progress!")
        if st.button("🎯 Browse Quizzes", type="primary"):
            st.switch_page("pages/1_Landing.py")

with tab2:
    st.header("🏆 My Badges")

    if badges:
        st.markdown("### Earned Badges")
        for badge in badges:
            st.markdown(f"<span class='badge'>{badge['badge_name']}</span>", unsafe_allow_html=True)
            st.caption(f"Earned on: {badge['earned_at']}")

        # Progress towards next badges
        st.markdown("---")
        st.subheader("🎯 Progress Towards Badges")

        # Check potential badges
        all_quizzes = get_all_quizzes()
        completed_quizzes = set(a["quiz_id"] for a in attempts)

        for grade in ["g1", "g2", "g3", "g4", "g5"]:
            grade_quizzes = [q for q in all_quizzes if q["grade"] == grade]
            if grade_quizzes:
                completed = sum(1 for q in grade_quizzes if q["id"] in completed_quizzes)
                total = len(grade_quizzes)

                if completed > 0 and completed < total:
                    st.markdown(f"**{GRADE_EMOJIS.get(grade, '📚')} {GRADE_NAMES.get(grade, grade)} Master**")
                    st.progress(completed / total)
                    st.markdown(f"{completed}/{total} quizzes completed\n")

    else:
        st.markdown("### 🏆 No badges yet!")
        st.info("Complete quizzes to earn badges. Here are some badges you can unlock:")

        st.markdown("""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px;">
            <h4>🎖️ Available Badges:</h4>
            <ul>
                <li>🌟 First Quiz Completed - Complete your first quiz</li>
                <li>⭐ Perfect Score - Get 100% on any quiz</li>
                <li>🏆 G1 Master - Complete all Grade 1 quizzes</li>
                <li>🌱 G2 Master - Complete all Grade 2 quizzes</li>
                <li>🚀 G3 Master - Complete all Grade 3 quizzes</li>
                <li>💎 G4 Master - Complete all Grade 4 quizzes</li>
                <li>🥇 G5 Master - Complete all Grade 5 quizzes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("📝 Attempt History")

    if attempts:
        # Show recent attempts
        st.subheader("Recent Activity")

        for attempt in attempts[:10]:
            quiz = next((q for q in get_all_quizzes() if q["id"] == attempt["quiz_id"]), None)
            if quiz:
                percentage = (attempt["score"] / attempt["total_questions"]) * 100

                emoji = "⭐" if percentage >= 80 else "📝" if percentage >= 60 else "🔄"

                st.markdown(f"""
                    <div class="progress-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{emoji} {quiz['title']}</strong><br>
                                <small>{attempt['completed_at']}</small>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.2rem; font-weight: bold; color: {'#4CAF50' if percentage >= 80 else '#FF9800' if percentage >= 60 else '#F44336'};">
                                    {percentage:.0f}%
                                </span><br>
                                <small>{attempt['score']}/{attempt['total_questions']}</small>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Full history table
        st.markdown("---")
        st.subheader("Full History")

        history_data = []
        for attempt in attempts:
            quiz = next((q for q in get_all_quizzes() if q["id"] == attempt["quiz_id"]), None)
            if quiz:
                history_data.append({
                    "Date": attempt["completed_at"],
                    "Quiz": quiz["title"],
                    "Score": f"{attempt['score']}/{attempt['total_questions']}",
                    "Percentage": f"{(attempt['score'] / attempt['total_questions']) * 100:.1f}%",
                    "Time (s)": attempt.get("time_spent", 0)
                })

        if history_data:
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download My History",
                data=csv,
                file_name=f"my_quiz_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No quiz attempts yet. Start your first quiz to see your history!")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; color: #999;">
        <p>📈 Keep learning and earning badges! 🏆</p>
    </div>
""", unsafe_allow_html=True)
