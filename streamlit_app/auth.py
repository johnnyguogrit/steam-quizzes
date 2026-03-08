"""
Authentication module for STEAM Quiz Platform.
Handles login, logout, and session management.
"""

import streamlit as st
from database import (
    authenticate_user, create_user, get_user, init_db, create_class,
    ANIMAL_PASSWORDS, get_class_by_code, authenticate_student, get_students_by_class_code
)


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


def show_student_login_page():
    """Display the child-friendly student login page with 3 steps."""
    # Initialize session state for login steps
    if "login_step" not in st.session_state:
        st.session_state.login_step = 1
    if "login_class_code" not in st.session_state:
        st.session_state.login_class_code = ""
    if "login_username" not in st.session_state:
        st.session_state.login_username = ""
    if "login_animal" not in st.session_state:
        st.session_state.login_animal = None

    # Custom CSS for child-friendly UI
    st.markdown("""
        <style>
        .login-step { background: white; border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .class-code-input { font-size: 2rem; text-align: center; letter-spacing: 5px; text-transform: uppercase; font-weight: bold; }
        .step-indicator { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .step-dot { width: 40px; height: 40px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .step-active { background: #FF6B9D; color: white; }
        .step-complete { background: #4CAF50; color: white; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 style="color: #FF6B9D; font-size: 2.5rem; text-align: center;">Student Login 学生登录</h1>', unsafe_allow_html=True)

        # Step indicator
        steps = [
            ("step-complete" if st.session_state.login_step > 1 else "step-active", "1"),
            ("step-active" if st.session_state.login_step == 2 else "step-complete" if st.session_state.login_step > 2 else "", "2"),
            ("step-active" if st.session_state.login_step == 3 else "", "3"),
        ]
        st.markdown(f"""
            <div class="step-indicator">
                <div class="step-dot {steps[0][0]}">{steps[0][1]}</div>
                <div class="step-dot {steps[1][0]}">{steps[1][1]}</div>
                <div class="step-dot {steps[2][0]}">{steps[2][1]}</div>
            </div>
        """, unsafe_allow_html=True)

        # Step 1: Class Code
        if st.session_state.login_step == 1:
            st.markdown('<h2 style="text-align: center;">Step 1: Enter Class Code</h2>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #666;">第一步：输入班级代码 (8个字母)</p>', unsafe_allow_html=True)

            class_code = st.text_input("Class Code", max_chars=8, key="student_class_code", label_visibility="collapsed")

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("Next 下一步", use_container_width=True, type="primary"):
                    if class_code and len(class_code) == 8:
                        if get_class_by_code(class_code.upper()):
                            st.session_state.login_class_code = class_code.upper()
                            st.session_state.login_step = 2
                            st.rerun()
                        else:
                            st.error("Class code not found. Please check with your teacher. 班级代码未找到，请询问老师。")
                    else:
                        st.warning("Please enter an 8-letter class code. 请输入8个字母的班级代码。")

        # Step 2: Username
        elif st.session_state.login_step == 2:
            st.markdown('<h2 style="text-align: center;">Step 2: Select Your Name</h2>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #666;">第二步：选择你的名字</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="text-align: center; color: #999;">Class: {st.session_state.login_class_code}</p>', unsafe_allow_html=True)

            students = get_students_by_class_code(st.session_state.login_class_code)

            if students:
                student_names = {s.get("full_name", s["username"]): s for s in students}
                selected_name = st.selectbox("Your Name 你的名字", options=list(student_names.keys()), key="student_name_select")

                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_a:
                    if st.button("Back 返回", use_container_width=True):
                        st.session_state.login_step = 1
                        st.rerun()
                with col_c:
                    if st.button("Next 下一步", use_container_width=True, type="primary"):
                        if selected_name:
                            st.session_state.login_username = student_names[selected_name]["username"]
                            st.session_state.login_step = 3
                            st.rerun()
            else:
                st.error("No students found in this class. 这个班级没有找到学生。")
                if st.button("Back 返回", use_container_width=True):
                    st.session_state.login_step = 1
                    st.rerun()

        # Step 3: Picture Password
        elif st.session_state.login_step == 3:
            st.markdown('<h2 style="text-align: center;">Step 3: Choose Your Picture Password</h2>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #666;">第三步：选择你的图片密码</p>', unsafe_allow_html=True)

            # 4x3 animal grid
            cols = st.columns(4)
            for idx, (num, animal) in enumerate(ANIMAL_PASSWORDS.items()):
                col_idx = idx % 4
                with cols[col_idx]:
                    selected = st.session_state.login_animal == num
                    # Use markdown to show emoji + text
                    label = f"{animal['emoji']} {animal['name']}\n{animal['chinese']}"
                    if st.button(
                        label,
                        key=f"animal_{num}",
                        use_container_width=True,
                        type="primary" if selected else "secondary"
                    ):
                        st.session_state.login_animal = num
                        st.rerun()

            st.markdown("---")
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_a:
                if st.button("Back 返回", use_container_width=True):
                    st.session_state.login_step = 2
                    st.rerun()
            with col_c:
                if st.button("Login 登录", use_container_width=True, type="primary", disabled=st.session_state.login_animal is None):
                    user = authenticate_student(
                        st.session_state.login_class_code,
                        st.session_state.login_username,
                        st.session_state.login_animal
                    )

                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["id"]
                        st.session_state.user_role = user["role"]
                        st.session_state.user_name = user["username"]
                        st.session_state.full_name = user.get("full_name", "")
                        st.session_state.class_id = user.get("class_id", "")
                        # Clear login state
                        for key in ["login_step", "login_class_code", "login_username", "login_animal"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("Wrong password. Password doesn't match. 密码错误，请重试。")

        # Teacher login link at bottom
        st.markdown("---")
        if st.button("Teacher Login 教师登录", use_container_width=True):
            for key in ["login_step", "login_class_code", "login_username", "login_animal"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("app.py")


def show_login_page():
    """Display login type selection (teacher vs student)."""
    st.set_page_config(page_title="STEAM Quiz Login", page_icon="🎓")

    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            color: #FF6B9D;
            font-size: 3rem;
            margin-bottom: 10px;
        }
        .login-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .role-card {
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="login-title">🎓 STEAM Quiz Login</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Choose your login type 选择登录方式</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #FFE0F0 0%, #FFF0F5 100%); border-radius: 20px; padding: 40px; text-align: center;">
                    <h2>👨‍🎓 Student</h2>
                    <p>学生登录</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Student Login\n学生登录", use_container_width=True, type="primary", key="goto_student_login"):
                show_student_login_page()

        with col2:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); border-radius: 20px; padding: 40px; text-align: center;">
                    <h2>👨‍🏫 Teacher</h2>
                    <p>教师登录</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Teacher Login\n教师登录", use_container_width=True, key="goto_teacher_login"):
                show_teacher_login_form_inline()

        st.markdown("""
            <div style="text-align: center; margin-top: 30px; color: #999;">
                <p>🌈 Spring 2026 STEAM Program</p>
            </div>
        """, unsafe_allow_html=True)


def show_teacher_login_form_inline():
    """Show teacher login form inline."""
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login 登录", "First Time Setup 首次设置"])

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
        st.info("👋 First time here? Create your admin account.")
        st.info("🔑 首次使用？请创建管理员账户。")

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


def logout_button():
    """Display a logout button in the sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
