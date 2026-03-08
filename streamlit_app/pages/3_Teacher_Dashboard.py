"""
Teacher Dashboard
Manage classes, view student progress, and export data.
"""

import streamlit as st
import pandas as pd
import io
from database import (
    get_user, create_user, get_classes_by_teacher, get_students_by_class,
    get_class_statistics, export_class_data, create_class, get_all_users,
    delete_user, delete_class, get_user_attempts, generate_graphical_password,
    batch_create_students, generate_username_from_name, get_connection, regenerate_class_passwords,
    get_user_by_username, get_animal_info, ANIMAL_PASSWORDS
)
from auth import require_teacher, logout_button, get_current_user

# Page config
st.set_page_config(
    page_title="Teacher Dashboard",
    page_icon="📊",
    layout="wide"
)

require_teacher()

# Initialize session state for storing student passwords
if 'student_passwords' not in st.session_state:
    st.session_state.student_passwords = {}  # {user_id: password}

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

    st.markdown("---")
    st.markdown("### 🐾 Animal Passwords")
    st.markdown("*Student password reference:*")
    # Display all 12 animals in a compact grid
    for num in range(1, 13):
        animal = ANIMAL_PASSWORDS[num]
        st.markdown(f"**{num}** {animal['emoji']} {animal['name']} {animal['chinese']}")


def create_credentials_pdf(class_name, students, password_map=None):
    """Create a PDF with class credentials, supporting Chinese and animal SVG icons.

    Args:
        class_name: Name of the class
        students: List of student dictionaries
        password_map: Optional dict mapping user_id to password (animal number 1-12)
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    # Container for the PDF elements
    elements = []

    # Get the assets directory path
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "animals")

    # Try to register Chinese font
    chinese_font_registered = False
    chinese_fonts = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]

    for font_path in chinese_fonts:
        try:
            if font_path == 'Helvetica':
                pdfmetrics.registerFont(TTFont('ChineseFont', 'Helvetica'))
            else:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            chinese_font_registered = True
            break
        except:
            continue

    # Define styles
    styles = getSampleStyleSheet()

    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parentStyle=styles['Heading1'],
        fontName='ChineseFont' if chinese_font_registered else 'Helvetica-Bold',
        fontSize=18,
        alignment=1,
        spaceAfter=8*mm
    )

    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parentStyle=styles['Normal'],
        fontName='ChineseFont' if chinese_font_registered else 'Helvetica',
        fontSize=9,
        alignment=1,
        spaceAfter=15*mm
    )

    # Add title
    elements.append(Paragraph(f"{class_name}", title_style))
    elements.append(Paragraph("班级学生登录凭证 / Student Login Credentials", subtitle_style))

    # Prepare table data with embedded SVG images
    # Headers: No., Name, Username, Password (with animal icon)
    table_data = [['No.', '姓名 / Name', '用户名 / Username', '密码 / Password']]

    for i, student in enumerate(students, 1):
        name = student.get("full_name", student["username"])
        username = student["username"]

        # Get password (animal number)
        password = student.get("password")
        if password is None and password_map:
            password = password_map.get(student["id"])

        if password and password.isdigit():
            animal_num = int(password)
            animal_info = get_animal_info(animal_num)
            # Create cell with animal emoji and name
            password_display = f"{animal_info['emoji']} {animal_info['name']} ({animal_info['chinese']})"
        else:
            password_display = "N/A"

        table_data.append([str(i), name, username, password_display])

    # Create table with adjusted column widths
    table = Table(table_data, colWidths=[12*mm, 35*mm, 30*mm, 50*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if chinese_font_registered else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10*mm),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'ChineseFont' if chinese_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 1), (-1, -1), 6*mm),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6*mm),
    ]))

    elements.append(table)

    # Add animal reference legend
    elements.append(Spacer(1, 10*mm))
    legend_style = ParagraphStyle(
        'Legend',
        parentStyle=styles['Normal'],
        fontName='ChineseFont' if chinese_font_registered else 'Helvetica',
        fontSize=8,
        alignment=1,
        spaceBefore=5*mm
    )
    elements.append(Paragraph("密码说明: 每个学生分配一个动物编号 (1-12)，登录时输入对应的数字即可", legend_style))

    # Add footer
    footer_style = ParagraphStyle(
        'Footer',
        parentStyle=styles['Normal'],
        fontName='ChineseFont' if chinese_font_registered else 'Helvetica',
        fontSize=7,
        alignment=1,
        spaceBefore=10*mm,
        textColor=colors.grey
    )
    elements.append(Paragraph("STEAM Quiz Platform | Spring 2026", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def create_user_with_password_storage(username, password, role, full_name, class_id):
    """Create a user and store the password in session state."""
    success = create_user(username, password, role, full_name, class_id)
    if success:
        # Get the newly created user ID
        user = get_user_by_username(username)
        if user:
            st.session_state.student_passwords[user["id"]] = password
    return success


def batch_create_students_with_password_storage(names, class_id):
    """Batch create students and store passwords in session state."""
    results = batch_create_students(names, class_id)

    # Store passwords for successful creations
    for r in results:
        if r["status"] == "success":
            user = get_user_by_username(r["username"])
            if user:
                st.session_state.student_passwords[user["id"]] = r["password"]

    return results


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
        selected_class_name = st.selectbox("Select Class", list(class_options.keys()), key="tab2_select_class")

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
                                # Clean up passwords from session state
                                students = get_students_by_class(str(cls["id"]))
                                for s in students:
                                    if s["id"] in st.session_state.student_passwords:
                                        del st.session_state.student_passwords[s["id"]]

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

                full_name = st.text_input("Student Name", key=f"tab2_student_name_{cls['id']}")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Add Student", key=f"add_single_{cls['id']}"):
                        if full_name:
                            username = generate_username_from_name(full_name, list(existing))
                            password = generate_graphical_password(1)

                            if create_user_with_password_storage(username, password, "student", full_name, str(cls["id"])):
                                animal_info = get_animal_info(int(password))
                                st.success(f"✅ Student '{full_name}' added! Username: {username}, Password: {animal_info['emoji']} {animal_info['name']} ({password})")
                                st.rerun()
                            else:
                                st.error("Failed to add student.")

                with col2:
                    if st.button("Generate Random Password", key=f"gen_{cls['id']}"):
                        pw = generate_graphical_password(1)
                        animal_info = get_animal_info(int(pw))
                        st.markdown(f"**Preview:** {animal_info['emoji']} {animal_info['name']} ({pw})")

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
                            results = batch_create_students_with_password_storage(names, str(cls["id"]))
                            success_count = sum(1 for r in results if r["status"] == "success")

                            st.markdown(f"### Results: {success_count}/{len(results)} students created")

                            for r in results:
                                if r["status"] == "success":
                                    animal_info = get_animal_info(int(r["password"]))
                                    st.markdown(f"✅ **{r['full_name']}** - `{r['username']}` / {animal_info['emoji']} {animal_info['name']} (`{r['password']}`)")
                                else:
                                    st.markdown(f"❌ **{r['full_name']}** - Failed")

                            if success_count > 0:
                                st.rerun()

            # Show students list
            students = get_students_by_class(str(cls["id"]))

            if students:
                st.markdown("#### Student List")

                # Download credentials buttons
                col1, col2 = st.columns(2)

                with col1:
                    # PDF download with Chinese and emoji support
                    # Use session state passwords
                    pdf_data = create_credentials_pdf(cls['name'], students, st.session_state.student_passwords)
                    st.download_button(
                        label="📄 Download Class Credentials (PDF)",
                        data=pdf_data,
                        file_name=f"{cls['name']}_credentials.pdf",
                        mime="application/pdf",
                        key=f"download_pdf_{cls['id']}"
                    )

                with col2:
                    # CSV download with animal passwords from session state
                    creds_data = []
                    for s in students:
                        pwd = st.session_state.student_passwords.get(s["id"], "N/A")
                        if pwd and pwd.isdigit():
                            animal_info = get_animal_info(int(pwd))
                            pwd_display = f"{animal_info['emoji']} {animal_info['name']} ({pwd})"
                        else:
                            pwd_display = pwd
                        creds_data.append({
                            "姓名": s.get("full_name", s["username"]),
                            "用户名": s["username"],
                            "密码": pwd_display
                        })
                    creds_df = pd.DataFrame(creds_data)
                    creds_csv = creds_df.to_csv(index=False).encode('utf-8-sig')  # UTF-8 with BOM for Excel compatibility
                    st.download_button(
                        label="📊 Download as CSV (Excel)",
                        data=creds_csv,
                        file_name=f"{cls['name']}_credentials.csv",
                        mime="text/csv",
                        key=f"download_csv_{cls['id']}"
                    )
                # Regenerate passwords section
                st.markdown("---")
                st.markdown("#### Password Management")
                if any(st.session_state.student_passwords.get(s["id"]) is None for s in students):
                    st.warning("⚠️ Some student passwords are not available. Click below to regenerate.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Regenerate All Passwords", key=f"regen_{cls['id']}", type="secondary"):
                        with st.spinner("Regenerating passwords..."):
                            results = regenerate_class_passwords(str(cls["id"]))
                            # Store new passwords in session state
                            for r in results:
                                st.session_state.student_passwords[r["user_id"]] = r["password"]
                            st.success(f"✅ Regenerated {len(results)} student passwords! Please download the PDF again.")
                            st.rerun()
                with col2:
                    st.markdown("**Note:** This will generate new random animal passwords for all students. Old passwords will no longer work!")
                # Student table with actions - show password if available
                for student in students:
                    pwd = st.session_state.student_passwords.get(student["id"], None)
                    # Display animal info if password exists
                    if pwd and pwd.isdigit():
                        animal_info = get_animal_info(int(pwd))
                        pwd_display = f"{animal_info['emoji']} {animal_info['name']} ({pwd})"
                    else:
                        pwd_display = "•••"
                    with st.expander(f"👤 {student.get('full_name', student['username'])}"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Username:** `{student['username']}`")
                            st.markdown(f"**Password:** {pwd_display}")
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
                                    # Clean up password from session state
                                    if student["id"] in st.session_state.student_passwords:
                                        del st.session_state.student_passwords[student["id"]]
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
            class_name = st.text_input("Class Name*", placeholder="e.g., Grade 1 - Class A", key="tab3_class_name")
            grade_level = st.selectbox("Grade Level*", ["G1", "G2", "G3", "G4", "G5"], key="tab3_grade_level")

        with col2:
            st.markdown("#### Step 2: Add Students (Optional)")
            st.markdown("Leave empty to create class without students.")
            names_input = st.text_area(
                "Paste student names (one per line or comma-separated)",
                placeholder="张三\n李四\n王五\n\nOr: 张三, 李四, 王五",
                height=150,
                key="tab3_names_input"
            )
            st.markdown("* Animal picture password will be auto-generated (e.g., 🐶 Dog, 🐱 Cat, 🐭 Mouse)")

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
                    results = batch_create_students_with_password_storage(names, str(class_id))
                    success_count = sum(1 for r in results if r["status"] == "success")

                    st.markdown(f"### 📊 Results: {success_count}/{len(results)} students added")

                    for r in results:
                        if r["status"] == "success":
                            animal_info = get_animal_info(int(r["password"]))
                            st.markdown(f"✅ **{r['full_name']}**")
                            st.markdown(f"   - Username: `{r['username']}` | Password: {animal_info['emoji']} {animal_info['name']} (`{r['password']}`)")
                        else:
                            st.markdown(f"❌ **{r['full_name']}** - Failed")

                    if success_count > 0:
                        st.balloons()
            else:
                st.info("👌 Class created without students. You can add students later in the 'Classes' tab.")

    st.markdown("---")
    if st.button("🔄 Create Another Class", use_container_width=True, key="tab3_create_another"):
        st.rerun()

with tab4:
    st.header("📤 Export Data")

    classes = get_classes_by_teacher(teacher["id"])

    if classes:
        # Select class to export
        class_options = {c["name"]: str(c["id"]) for c in classes}
        selected_class_name = st.selectbox("Select Class", list(class_options.keys()), key="tab4_select_class")

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
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"{selected_class_name}_quiz_data.csv",
                        mime="text/csv",
                        key="tab4_download_csv"
                    )

                with col2:
                    # Convert to Excel using BytesIO
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Quiz Data')
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Download as Excel",
                        data=buffer,
                        file_name=f"{selected_class_name}_quiz_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="tab4_download_excel"
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
