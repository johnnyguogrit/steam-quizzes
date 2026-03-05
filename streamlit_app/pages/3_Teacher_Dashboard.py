"""
Teacher Dashboard
Manage classes, view student progress, and export data.
"""

import streamlit as st
import pandas as pd
from database import (
    get_user, create_user, get_classes_by_teacher, get_students_by_class,
    get_class_statistics, export_class_data, create_class, get_all_users,
    delete_user, delete_class, get_user_attempts, generate_graphical_password,
    batch_create_students, generate_username_from_name, get_connection
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
    .password-display {
        font-size: 2rem;
        text-align: center;
        padding: 15px;
        background: #f0f8ff;
        border-radius: 10px;
        margin: 10px 0;
        letter-spacing: 10px;
    }
    .success-row {
        background: #d4edda;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .error-row {
        background: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Classes", "➕ Create Class & Add Students", "📤 Export"])

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
        st.info("👋 You don't have any classes yet. Go to 'Create Class & Add Students' to create your first class!")

with tab2:
    st.header("👥 Manage Classes & Students")

    classes = get_classes_by_teacher(teacher["id"])

    if not classes:
        st.info("No classes found. Go to 'Create Class & Add Students' to create your first class!")
    else:
        # Select class to view/manage
        class_options = {c["name"]: c for c in classes}
        selected_class_name = st.selectbox("Select Class", list(class_options.keys()))

        if selected_class_name:
            cls = class_options[selected_class_name]
            student_count = cls.get("student_count", 0)

            st.markdown(f"### 📚 {cls['name']} - {student_count} student{'s' if student_count != 1 else ''}")
            st.markdown(f"**Grade Level:** {cls.get('grade_level', 'N/A')}")

            st.markdown("---")

            # Delete class section
            delete_key = f"delete_class_{cls['id']}"
            confirm_key = f"confirm_delete_{cls['id']}"

            if confirm_key not in st.session_state:
                st.session_state[confirm_key] = False

            if not st.session_state[confirm_key]:
                if st.button(f"🗑 Delete Class", key=delete_key, type="secondary"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
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
            st.markdown("#### Students in this class")

            # Add students to this class
            with st.expander("➕ Add more students to this class", expanded=False):
                st.markdown("**Option 1: Add Single Student**")

                # Get existing usernames
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users")
                existing = set(row[0] for row in cursor.fetchall())
                conn.close()

                full_name = st.text_input("Student Name")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Add Student", key=f"add_single_{cls['id']}"):
                        if full_name:
                            username = generate_username_from_name(full_name, list(existing))
                            password = generate_graphical_password(1)

                            if create_user(username, password, "student", full_name, str(cls["id"])):
                                st.success(f"✅ Student '{full_name}' added! Username: {username}, Password: {password}")
                                st.rerun()
                            else:
                                st.error("Failed to add student.")

                with col2:
                    if st.button("Generate Random Password", key=f"gen_{cls['id']}"):
                    pw = generate_graphical_password(1)
                    st.markdown(f"**Preview:** `{pw}`")

            st.markdown("**Option 2: Batch Import Students**")

            names_input = st.text_area(
                "Paste student names (one per line or comma-separated)",
                placeholder="张三\n李四\n王五\n\nOr: 张三, 李四, 王五",
                height=100,
                key=f"batch_{cls['id']}"
            )

            if st.button("✨ Batch Import", key=f"batch_import_{cls['id']}", type="primary"):
                if names_input.strip():
                    # Parse names
                    names = []
                    for line in names_input.strip().split('\n'):
                        line_names = [n.strip() for n in line.split(',') if n.strip()]
                        names.extend(line_names)

                    if names:
                        results = batch_create_students(names, str(cls["id"]))
                        success_count = sum(1 for r in results if r["status"] == "success")

                        st.markdown(f"### Results: {success_count}/{len(results)} students created")

                        for r in results:
                            if r["status"] == "success":
                                st.markdown(f"✅ **{r['full_name']}** - `{r['username']}` / `{r['password']}`")
                            else:
                                st.markdown(f"❌ **{r['full_name']}** - Failed")

                        if success_count > 0:
                            st.rerun()

            # Show students list
            students = get_students_by_class(str(cls["id"]))

            if students:
                st.markdown("#### Student List")

                # Download credentials button
                creds_data = [{
                    "姓名": s.get("full_name", s["username"]),
                    "用户名": s["username"],
                    "密码": s.get("password", "N/A")  # Note: password_hash is stored, not plain password
                } for s in students]

                if st.button("📥 Download Class Credentials", key=f"download_creds_{cls['id']}"):
                    df = pd.DataFrame(creds_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"{cls['name']}_credentials.csv",
                        mime="text/csv",
                        key=f"dl_{cls['id']}"
                    )

                # Student table with actions
                for student in students:
                    with st.expander(f"👤 {student.get('full_name', student['username'])}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Username:** `{student['username']}`")
                        st.markdown(f"**Attempts:** {student.get('total_attempts', 0)}")
                        if student.get("avg_score"):
                            st.markdown(f"**Avg Score:** {student.get('avg_score', 0) * 100:.1f}%")

                    with col2:
                        if st.button("📈 View Progress", key=f"progress_{student['id']}"):
                            st.session_state.viewing_student_id = student['id']
                            st.info("View progress feature coming soon!")

                    with col3:
                        if st.button("🗑 Remove", key=f"remove_{student['id']}", type="secondary"):
                            if delete_user(student["id"]):
                                st.success("Student removed!")
                                st.rerun()
                            else:
                                st.error("Failed to remove student.")
            else:
                st.info("No students in this class yet. Add students above!")

with tab3:
    st.header("➕ Create New Class & Add Students")

    st.markdown("""
    ### Create a new class and add students in one place!
    """)

    # Step 1: Create Class
    with st.form("create_class_and_students"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Step 1: Create Class")
            class_name = st.text_input("Class Name*", placeholder="e.g., Grade 1 - Class A")
            grade_level = st.selectbox("Grade Level*", ["G1", "G2", "G3", "G4", "G5"])

        with col2:
            st.markdown("#### Step 2: Add Students (Optional)")
            st.markdown("Leave empty to create class without students.")
            names_input = st.text_area(
                "Paste student names (one per line or comma-separated)",
                placeholder="张三\n李四\n王五\n\nOr: 张三, 李四, 王五",
                height=150
            )
            st.markdown("* Single emoji password will be auto-generated (e.g., 🌟, 🎮, 🍎)")

        submitted = st.form_submit_button("Create Class & Add Students", type="primary")

        if submitted and class_name:
            # Create the class first
            class_id = create_class(class_name, grade_level, teacher["id"])

            st.success(f"✅ Class '{class_name}' created successfully!")

            # Then add students if provided
            if names_input.strip():
                # Parse names
                names = []
                for line in names_input.strip().split('\n'):
                    line_names = [n.strip() for n in line.split(',') if n.strip()]
                    names.extend(line_names)

                if names:
                    results = batch_create_students(names, str(class_id))
                    success_count = sum(1 for r in results if r["status"] == "success")

                    st.markdown(f"### 📊 Results: {success_count}/{len(results)} students added")

                    for r in results:
                        if r["status"] == "success":
                            st.markdown(f"✅ **{r['full_name']}**")
                            st.markdown(f"   - Username: `{r['username']}` | Password: `{r['password']}`")
                        else:
                            st.markdown(f"❌ **{r['full_name']}** - Failed")

                    if success_count > 0:
                        st.balloons()
            else:
                st.info("👌 Class created without students. You can add students later in the 'Classes' tab.")

            st.markdown("---")
            if st.button("🔄 Create Another", use_container_width=True):
                st.rerun()

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
