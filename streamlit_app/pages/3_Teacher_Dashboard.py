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
    batch_create_students
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
    .password-preview {
        font-size: 1.5rem;
        text-align: center;
        padding: 15px;
        background: #f0f8ff;
        border-radius: 10px;
        margin: 10px 0;
        letter-spacing: 5px;
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

                    # Student table with passwords
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

    create_tab1, create_tab2, create_tab3 = st.tabs(["📚 New Class", "👨‍🎓 Single Student", "📋 Batch Import"])

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
        st.subheader("Create Single Student Account")
        st.info("💡 A graphical password will be auto-generated (e.g., 🌟)")

        # Select class
        classes = get_classes_by_teacher(teacher["id"])

        if classes:
            with st.form("create_student_form"):
                full_name = st.text_input("Full Name*", placeholder="Student's full name")

                # Show password preview option
                show_preview = st.checkbox("Preview password", value=True)

                class_options = {f"{c['name']} ({c.get('grade_level', 'N/A')})": str(c["id"]) for c in classes}
                selected_class = st.selectbox("Class*", list(class_options.keys()))

                submitted = st.form_submit_button("Create Student", type="primary")

                if submitted and full_name:
                    # Generate username and password
                    from database import generate_username_from_name

                    class_id = class_options[selected_class]

                    # Get existing usernames
                    conn = __import__('database').get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM users")
                    existing = set(row[0] for row in cursor.fetchall())
                    conn.close()

                    username = generate_username_from_name(full_name, list(existing))
                    password = generate_graphical_password(4)

                    if create_user(username, password, "student", full_name, class_id):
                        st.success(f"Student '{full_name}' created successfully! 🎉")

                        # Show credentials
                        if show_preview:
                            st.markdown(f"""
                                <div class="password-preview">
                                    <strong>Username:</strong> {username}<br>
                                    <strong>Password:</strong> {password}
                                </div>
                            """, unsafe_allow_html=True)

                        st.info(f"Share these credentials with the student:\n- Username: {username}\n- Password: {password}")
                        st.balloons()
                    else:
                        st.error("Failed to create student. Please try again.")
        else:
            st.warning("Please create a class first before adding students.")

    with create_tab3:
        st.subheader("📋 Batch Import Students")
        st.info("💡 Paste student names from Excel (one name per line or separated by commas)")
        st.markdown("""
        **Instructions:**
        1. Select the target class
        2. Paste student names (from Excel column or type manually)
        3. Click "Generate & Create Students"
        4. Download the credentials list to share with students

        Each student will get:
        - Auto-generated username (based on their name)
        - Graphical password (e.g., 🌟)
        """)

        # Select class
        classes = get_classes_by_teacher(teacher["id"])

        if classes:
            class_options = {f"{c['name']} ({c.get('grade_level', 'N/A')})": str(c["id"]) for c in classes}
            selected_class = st.selectbox("Select Class*", list(class_options.keys()))
            class_id = class_options[selected_class]

            # Input area for student names
            names_input = st.text_area(
                "Paste Student Names",
                placeholder="张三\n李四\n王五\n\nOr separated by commas:\n张三, 李四, 王五",
                height=150,
                help="Enter one name per line, or separate with commas"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✨ Generate & Create Students", type="primary", use_container_width=True):
                    if names_input.strip():
                        # Parse names - handle both newlines and commas
                        names = []
                        for line in names_input.strip().split('\n'):
                            # Split by comma and strip whitespace
                            line_names = [n.strip() for n in line.split(',') if n.strip()]
                            names.extend(line_names)

                        if names:
                            # Batch create
                            results = batch_create_students(names, class_id)

                            # Show results
                            success_count = sum(1 for r in results if r["status"] == "success")
                            fail_count = len(results) - success_count

                            st.markdown(f"### Results: {success_count} created, {fail_count} failed")

                            # Show each result
                            for r in results:
                                if r["status"] == "success":
                                    st.markdown(f"""
                                        <div class="success-row">
                                            ✅ <strong>{r['full_name']}</strong><br>
                                            Username: <code>{r['username']}</code> | Password: <code>{r['password']}</code>
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                        <div class="error-row">
                                            ❌ <strong>{r['full_name']}</strong> - Failed to create
                                        </div>
                                    """, unsafe_allow_html=True)

                            if success_count > 0:
                                st.balloons()

                                # Create downloadable credentials
                                creds_df = pd.DataFrame([
                                    {"姓名": r["full_name"], "用户名": r["username"], "密码": r["password"]}
                                    for r in results if r["status"] == "success"
                                ])

                                csv = creds_df.to_csv(index=False)
                                st.download_button(
                                    "📥 Download Credentials List",
                                    csv,
                                    f"students_credentials_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                        else:
                            st.warning("No valid names found. Please check your input.")
                    else:
                        st.warning("Please enter student names first.")

            with col2:
                st.markdown("**Password Examples:**")
                st.markdown("""
                    <div class="password-preview">
                        🌟
                    </div>
                    <div class="password-preview">
                        🎮
                    </div>
                    <div class="password-preview">
                        🍎
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("**Tips:**")
                st.markdown("- Use graphical passwords - easy to remember!")
                st.markdown("- Each password is 1 random emoji")
                st.markdown("- Download the credentials list after creating")

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
