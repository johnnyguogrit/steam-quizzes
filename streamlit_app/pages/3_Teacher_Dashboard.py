"""
Teacher Dashboard
Manage classes, view student progress, and export data.
"""

import streamlit as st
import pandas as pd
from database import (
    get_user, create_user, get_classes_by_teacher, get_students_by_class,
    get_class_statistics, export_class_data, create_class, get_all_users,
    delete_user, delete_class, get_user_attempts
)
from auth import require_teacher, logout_button, get_current_user

# Page config
st.set_page_config(
    page_title="Teacher Dashboard",
    page_icon="📊",
    layout="wide"
)

require_teacher()

# Sidebar
with st.sidebar:
    st.title("👨‍🏫 Teacher Dashboard")
    st.markdown(f"👤 {st.session_state.full_name or st.session_state.user_name}")
    st.markdown("---")
    logout_button()

    st.markdown("### Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🎯 Browse Quizzes", use_container_width=True):
        st.switch_page("pages/1_Landing.py")

# Custom CSS
st.markdown("""
<style>
    .stat-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .delete-warning {
        padding: 15px;
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Classes", "➕ Create", "📤 Export"])

# Get current teacher
teacher = get_current_user()

with tab1:
    st.header("📊 Overview")

    classes = get_classes_by_teacher(teacher["id"])

    if classes:
        # Calculate overall statistics
        total_students = sum(c["student_count"] for c in classes)
        total_classes = len(classes)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Classes", total_classes)
        with col2:
            st.metric("Total Students", total_students)

        # Class performance
        st.subheader("Class Performance")

        for cls in classes:
            with st.expander(f"📚 {cls['name']}"):
                stats = get_class_statistics(str(cls["id"]))

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Students", stats["total_students"])
                with col2:
                    st.metric("Total Attempts", stats["total_attempts"])
                with col3:
                    st.metric("Avg Score", f"{stats['average_score']}%")
                with col4:
                    if stats["total_attempts"] > 0:
                        completion = (stats["total_attempts"] / (stats["total_students"] * 40)) * 100
                        st.metric("Quiz Completion", f"{completion:.1f}%")

    else:
        st.info("👋 You don't have any classes yet. Create your first class in the 'Create' tab!")

with tab2:
    st.header("👥 Manage Classes")

    classes = get_classes_by_teacher(teacher["id"])

    if classes:
        for cls in classes:
            student_count = cls.get("student_count", 0)
            class_header = f"📚 {cls['name']} - {student_count} student{'s' if student_count != 1 else ''}"

            with st.expander(class_header):
                st.markdown(f"**Grade Level:** {cls.get('grade_level', 'N/A')}")

                # Delete class section
                st.markdown("---")

                # Use a container for delete UI
                delete_key = f"delete_class_{cls['id']}"
                confirm_key = f"confirm_delete_{cls['id']}"

                # Initialize session state
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:
                    # Show delete button
                    if st.button(f"🗑 Delete Class", key=delete_key, type="secondary"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    # Show confirmation UI
                    st.markdown(f"""
                        <div class="delete-warning">
                            <strong>⚠️ Warning:</strong> You are about to delete the class <strong>"{cls['name']}"</strong>.<br>
                            This will also delete all {student_count} student{'s' if student_count != 1 else ''} in this class and all their data!<br>
                            <strong>This action cannot be undone!</strong>
                        </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Confirm Delete", key=f"ok_{cls['id']}", type="primary"):
                            try:
                                if delete_class(cls["id"]):
                                    st.success(f"Class '{cls['name']}' deleted successfully!")
                                    # Clear the confirmation state
                                    if confirm_key in st.session_state:
                                        del st.session_state[confirm_key]
                                    st.rerun()
                                else:
                                    st.error("Failed to delete class.")
                            except Exception as e:
                                st.error(f"Error deleting class: {e}")

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{cls['id']}"):
                            if confirm_key in st.session_state:
                                del st.session_state[confirm_key]
                            st.rerun()

                st.markdown("---")

                # Show students
                students = get_students_by_class(str(cls["id"]))

                if students:
                    st.markdown("##### Students:")

                    # Student table
                    student_data = []
                    for s in students:
                        student_data.append({
                            "Name": s.get("full_name", s["username"]),
                            "Username": s["username"],
                            "Attempts": s.get("total_attempts", 0),
                            "Avg Score": f"{s.get('avg_score', 0) * 100:.1f}%" if s.get("avg_score") else "N/A"
                        })

                    df = pd.DataFrame(student_data)
                    st.dataframe(df, use_container_width=True)

                    # Student actions
                    selected_student = st.selectbox(
                        "Select student to manage:",
                        options=[s["id"] for s in students],
                        format_func=lambda x: next((s["full_name"] or s["username"] for s in students if s["id"] == x), str(x)),
                        key=f"select_student_{cls['id']}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Progress", key=f"view_{cls['id']}_{selected_student}"):
                            st.session_state.viewing_student_id = selected_student
                            st.rerun()
                    with col2:
                        if st.button("🗑 Remove Student", key=f"remove_{cls['id']}_{selected_student}"):
                            if delete_user(selected_student):
                                st.success("Student removed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to remove student.")
                else:
                    st.info("No students in this class yet.")
    else:
        st.info("No classes found. Create your first class in the 'Create' tab!")

with tab3:
    st.header("➕ Create")

    create_tab1, create_tab2 = st.tabs(["📚 New Class", "👨‍🎓 New Student"])

    with create_tab1:
        st.subheader("Create a New Class")

        with st.form("create_class_form"):
            class_name = st.text_input("Class Name*", placeholder="e.g., Grade 1 - Class A")
            grade_level = st.selectbox("Grade Level*", ["G1", "G2", "G3", "G4", "G5"])

            submitted = st.form_submit_button("Create Class", type="primary")

            if submitted and class_name:
                class_id = create_class(class_name, grade_level, teacher["id"])
                st.success(f"Class '{class_name}' created successfully! 🎉")
                st.balloons()
                st.rerun()

    with create_tab2:
        st.subheader("Create Student Account")

        # Select class
        classes = get_classes_by_teacher(teacher["id"])

        if classes:
            with st.form("create_student_form"):
                username = st.text_input("Username*", placeholder="Student's username")
                password = st.text_input("Password*", type="password")
                full_name = st.text_input("Full Name", placeholder="Student's full name")

                class_options = {f"{c['name']} ({c.get('grade_level', 'N/A')})": str(c["id"]) for c in classes}
                selected_class = st.selectbox("Class*", list(class_options.keys()))

                submitted = st.form_submit_button("Create Student", type="primary")

                if submitted and username and password:
                    class_id = class_options[selected_class]
                    if create_user(username, password, "student", full_name, class_id):
                        st.success(f"Student '{full_name or username}' created successfully! 🎉")
                        st.info(f"Share these credentials with the student:\n- Username: {username}\n- Password: {password}")
                        st.balloons()
                    else:
                        st.error("Username already exists. Please choose a different username.")
        else:
            st.warning("Please create a class first before adding students.")

with tab4:
    st.header("📤 Export Data")

    classes = get_classes_by_teacher(teacher["id"])

    if classes:
        # Select class to export
        class_options = {c["name"]: str(c["id"]) for c in classes}
        selected_class_name = st.selectbox("Select Class", list(class_options.keys()))

        if selected_class_name:
            class_id = class_options[selected_class_name]

            # Get export data
            export_data = export_class_data(class_id)

            if export_data:
                df = pd.DataFrame(export_data)

                st.subheader(f"📊 Data for {selected_class_name}")
                st.dataframe(df, use_container_width=True)

                # Export buttons
                col1, col2 = st.columns(2)

                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"{selected_class_name}_quiz_data.csv",
                        mime="text/csv"
                    )

                with col2:
                    # Convert to Excel
                    output = pd.ExcelWriter(f"{selected_class_name}_quiz_data.xlsx", engine='openpyxl')
                    df.to_excel(output, index=False, sheet_name='Quiz Data')
                    output.close()

                    with open(f"{selected_class_name}_quiz_data.xlsx", 'rb') as f:
                        st.download_button(
                            label="📥 Download as Excel",
                            data=f,
                            file_name=f"{selected_class_name}_quiz_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No quiz data available for this class yet.")
    else:
        st.info("No classes found. Create a class first.")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; color: #999;">
        <p>📚 Teacher Dashboard | Spring 2026 STEAM Program</p>
    </div>
""", unsafe_allow_html=True)
