"""
Database operations for STEAM Quiz Platform.
Uses SQLite for user management and quiz tracking.
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Optional, Dict, List

# Database path - use persistent storage on Streamlit Cloud
# Streamlit Cloud provides /mount/data for persistent storage
if os.path.exists("/mount/data"):
    # Running on Streamlit Cloud - use persistent storage
    DB_DIR = "/mount/data"
else:
    # Running locally - use local data directory
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

DB_PATH = os.path.join(DB_DIR, "users.db")


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # Users table (teachers and students)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
            full_name TEXT,
            class_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Classes table (for teacher management)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade_level TEXT,
            teacher_id INTEGER,
            class_code TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    """)

    # Quiz attempts tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id TEXT NOT NULL,
            score INTEGER,
            total_questions INTEGER,
            time_spent INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Quiz version tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id TEXT NOT NULL,
            version TEXT,
            content_hash TEXT,
            deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Badges/achievements for students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_type TEXT NOT NULL,
            badge_name TEXT NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, badge_type)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# Animal password configuration (12 animals for student passwords)
ANIMAL_PASSWORDS = {
    1: {"name": "Dog", "chinese": "狗", "emoji": "🐶"},
    2: {"name": "Cat", "chinese": "猫", "emoji": "🐱"},
    3: {"name": "Mouse", "chinese": "老鼠", "emoji": "🐭"},
    4: {"name": "Rabbit", "chinese": "兔子", "emoji": "🐰"},
    5: {"name": "Fox", "chinese": "狐狸", "emoji": "🦊"},
    6: {"name": "Bear", "chinese": "熊", "emoji": "🐻"},
    7: {"name": "Panda", "chinese": "熊猫", "emoji": "🐼"},
    8: {"name": "Koala", "chinese": "考拉", "emoji": "🐨"},
    9: {"name": "Lion", "chinese": "狮子", "emoji": "🦁"},
    10: {"name": "Monkey", "chinese": "猴子", "emoji": "🐵"},
    11: {"name": "Frog", "chinese": "青蛙", "emoji": "🐸"},
    12: {"name": "Zebra", "chinese": "斑马", "emoji": "🦓"},
}

# Memorable 8-letter words for class codes
CLASS_CODE_WORDS = [
    "PLANET", "GALAXY", "JUNGLE", "OCEAN", "FOREST",
    "CASTLE", "DRAGON", "WIZARD", "KINGDOM", "VALLEY",
    "SUNSHINE", "RAINBOW", "THUNDER", "DIAMOND", "CRYSTAL",
    "VOLCANO", "GLACIER", "CANYON", "MOUNTAIN", "RIVER",
    "PENGUIN", "DOLPHIN", "BUTTERFLY", "ELEPHANT", "GIRAFFE"
]


def get_animal_info(animal_number: int) -> dict:
    """Get animal information by number."""
    return ANIMAL_PASSWORDS.get(animal_number, ANIMAL_PASSWORDS[1])


def get_animal_by_name(animal_name: str) -> int:
    """Get animal number by name (case-insensitive)."""
    for num, info in ANIMAL_PASSWORDS.items():
        if info["name"].lower() == animal_name.lower():
            return num
    return 1


# Class code functions for student login

def generate_unique_class_code() -> str:
    """Generate a unique 8-letter class code."""
    import random
    while True:
        code = random.choice(CLASS_CODE_WORDS)
        if not get_class_by_code(code):
            return code


def get_class_by_code(class_code: str) -> Optional[Dict]:
    """Get class by class code."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes WHERE class_code = ?", (class_code,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def get_students_by_class_code(class_code: str) -> List[Dict]:
    """Get all students for a class using class code."""
    cls = get_class_by_code(class_code)
    if not cls:
        return []
    return get_students_by_class(str(cls["id"]))


def authenticate_student(class_code: str, username: str, animal_number: int) -> Optional[Dict]:
    """Authenticate student using class code, username, and animal password."""
    cls = get_class_by_code(class_code)
    if not cls:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, username, password_hash, role, full_name, class_id
           FROM users WHERE username = ? AND class_id = ? AND role = 'student'
        """,
        (username, str(cls["id"]))
    )
    user = cursor.fetchone()
    conn.close()

    if user and user["password_hash"] == hash_password(str(animal_number)):
        return dict(user)
    return None


def generate_graphical_password(length: int = 1) -> str:
    """Generate a random graphical password using animal numbers.

    Returns a random number 1-12 representing an animal that students can easily remember.
    Examples: 1 (Dog), 2 (Cat), 3 (Mouse)
    """
    import random
    return str(random.randint(1, 12))


def generate_username_from_name(full_name: str, existing_names: list = None) -> str:
    """Generate a unique username from student's full name.

    Converts Chinese name to pinyin-style username: zhangsan1, lisi2, etc.
    """
    import random
    import string

    if existing_names is None:
        existing_names = []

    # For Chinese names, use phonetic approximation
    # For simplicity, we'll use a combination approach
    base_name = full_name.lower().replace(' ', '_')

    # Remove any non-alphanumeric characters
    base_name = ''.join(c for c in base_name if c.isalnum() or c == '_')

    # If base_name is too short or empty, use default
    if len(base_name) < 2:
        base_name = 'student'

    # Try base_name first, then add numbers
    username = base_name
    counter = 1
    while username in existing_names:
        username = f"{base_name}{counter}"
        counter += 1

    return username


def create_user(username: str, password: str, role: str, full_name: str = "", class_id: str = "") -> bool:
    """Create a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, full_name, class_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, hash_password(password), role, full_name, class_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user and return user data if valid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, username, password_hash, role, full_name, class_id
        FROM users WHERE username = ?
        """,
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user and user["password_hash"] == hash_password(password):
        return dict(user)
    return None


def get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_class(name: str, grade_level: str, teacher_id: int) -> int:
    """Create a new class with auto-generated class code."""
    conn = get_connection()
    cursor = conn.cursor()

    # Generate unique class code
    class_code = generate_unique_class_code()

    cursor.execute(
        "INSERT INTO classes (name, grade_level, teacher_id, class_code) VALUES (?, ?, ?, ?)",
        (name, grade_level, teacher_id, class_code)
    )
    conn.commit()
    class_id = cursor.lastrowid
    conn.close()
    return class_id


def get_classes_by_teacher(teacher_id: int) -> List[Dict]:
    """Get all classes for a teacher."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, COUNT(u.id) as student_count
        FROM classes c
        LEFT JOIN users u ON u.class_id = CAST(c.id AS TEXT) AND u.role = 'student'
        WHERE c.teacher_id = ?
        GROUP BY c.id
        ORDER BY c.name
        """,
        (teacher_id,)
    )
    classes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return classes


def get_students_by_class(class_id: str) -> List[Dict]:
    """Get all students in a class."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.*,
               COUNT(qa.id) as total_attempts,
               AVG(CAST(qa.score AS REAL) / CAST(qa.total_questions AS REAL)) as avg_score
        FROM users u
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
        WHERE u.class_id = ? AND u.role = 'student'
        GROUP BY u.id
        ORDER BY u.full_name
        """,
        (class_id,)
    )
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students


def record_quiz_attempt(user_id: int, quiz_id: str, score: int, total_questions: int, time_spent: int = 0) -> int:
    """Record a quiz attempt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, time_spent)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, quiz_id, score, total_questions, time_spent)
    )
    conn.commit()
    attempt_id = cursor.lastrowid

    # Check for badges
    _check_and_award_badges(cursor, user_id, quiz_id, score, total_questions)

    conn.commit()
    conn.close()
    return attempt_id


def _check_and_award_badges(cursor, user_id: int, quiz_id: str, score: int, total_questions: int):
    """Check and award badges based on performance."""
    percentage = score / total_questions if total_questions > 0 else 0

    # Perfect score badge
    if percentage >= 1.0:
        cursor.execute(
            """
            INSERT OR IGNORE INTO badges (user_id, badge_type, badge_name)
            VALUES (?, 'perfect_score', 'Perfect Score! ???')
            """,
            (user_id,)
        )

    # First quiz badge
    cursor.execute(
        """
        INSERT OR IGNORE INTO badges (user_id, badge_type, badge_name)
        SELECT ?, 'first_quiz', 'First Quiz Completed ???'
        WHERE NOT EXISTS (SELECT 1 FROM quiz_attempts WHERE user_id = ? AND id != ?)
        """,
        (user_id, user_id, cursor.lastrowid)
    )

    # Check for completing all quizzes in a grade/unit
    conn = get_connection()
    grade = quiz_id.split('-')[0]  # e.g., 'g1'
    cursor.execute(
        """
        SELECT COUNT(DISTINCT quiz_id) as completed_count
        FROM quiz_attempts
        WHERE user_id = ? AND quiz_id LIKE ?
        """,
        (user_id, f"{grade}%")
    )
    result = cursor.fetchone()
    if result and result['completed_count'] >= 8:  # 8 quizzes per grade
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO badges (user_id, badge_type, badge_name)
            VALUES (?, '{grade}_complete', 'Grade {grade.upper()} Master! ???')
            """,
            (user_id,)
        )


def get_user_attempts(user_id: int) -> List[Dict]:
    """Get all quiz attempts for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT qa.*,
               (CAST(score AS REAL) / total_questions) * 100 as percentage
        FROM quiz_attempts qa
        WHERE qa.user_id = ?
        ORDER BY qa.completed_at DESC
        """,
        (user_id,)
    )
    attempts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return attempts


def get_quiz_attempts_by_quiz(user_id: int, quiz_id: str) -> List[Dict]:
    """Get all attempts for a specific quiz by a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM quiz_attempts
        WHERE user_id = ? AND quiz_id = ?
        ORDER BY completed_at DESC
        """,
        (user_id, quiz_id)
    )
    attempts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return attempts


def get_class_statistics(class_id: str) -> Dict:
    """Get statistics for a class."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total students
    cursor.execute(
        "SELECT COUNT(*) as count FROM users WHERE class_id = ? AND role = 'student'",
        (class_id,)
    )
    total_students = cursor.fetchone()["count"]

    # Total attempts
    cursor.execute(
        """
        SELECT COUNT(*) as count FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        WHERE u.class_id = ?
        """,
        (class_id,)
    )
    total_attempts = cursor.fetchone()["count"]

    # Average score
    cursor.execute(
        """
        SELECT AVG(CAST(qa.score AS REAL) / qa.total_questions) as avg_score
        FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        WHERE u.class_id = ?
        """,
        (class_id,)
    )
    avg_score = cursor.fetchone()["avg_score"] or 0

    # Quizzes by performance
    cursor.execute(
        """
        SELECT qa.quiz_id,
               COUNT(*) as attempts,
               AVG(CAST(qa.score AS REAL) / qa.total_questions) as avg_score
        FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        WHERE u.class_id = ?
        GROUP BY qa.quiz_id
        ORDER BY quiz_id
        """,
        (class_id,)
    )
    quiz_performance = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_students": total_students,
        "total_attempts": total_attempts,
        "average_score": round(avg_score * 100, 1),
        "quiz_performance": quiz_performance
    }


def export_class_data(class_id: str) -> List[Dict]:
    """Export all student data for a class."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.username, u.full_name, u.class_id,
               qa.quiz_id, qa.score, qa.total_questions,
               (CAST(qa.score AS REAL) / qa.total_questions) * 100 as percentage,
               qa.completed_at
        FROM users u
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
        WHERE u.class_id = ? AND u.role = 'student'
        ORDER BY u.full_name, qa.completed_at
        """,
        (class_id,)
    )
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data


def update_user_password(user_id: int, new_password: str) -> bool:
    """Update user password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(new_password), user_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_user(user_id: int) -> bool:
    """Delete a user and all their data."""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete related records first
    cursor.execute("DELETE FROM quiz_attempts WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM badges WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def delete_class(class_id: int) -> bool:
    """Delete a class and all its students."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First, get all students in this class
        cursor.execute("SELECT id FROM users WHERE class_id = ?", (str(class_id),))
        student_ids = [row[0] for row in cursor.fetchall()]

        # Delete all data for each student
        for student_id in student_ids:
            cursor.execute("DELETE FROM quiz_attempts WHERE user_id = ?", (student_id,))
            cursor.execute("DELETE FROM badges WHERE user_id = ?", (student_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))

        # Delete the class
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_users(role: Optional[str] = None) -> List[Dict]:
    """Get all users, optionally filtered by role."""
    conn = get_connection()
    cursor = conn.cursor()
    if role:
        cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY created_at DESC", (role,))
    else:
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def get_user_badges(user_id: int) -> List[Dict]:
    """Get all badges for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM badges WHERE user_id = ? ORDER BY earned_at DESC", (user_id,))
    badges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return badges


def get_quiz_summary(user_id: int, quiz_id: str) -> Dict:
    """Get summary of user's performance on a quiz."""
    attempts = get_quiz_attempts_by_quiz(user_id, quiz_id)
    if not attempts:
        return {"attempts": 0, "best_score": 0, "avg_score": 0, "last_attempt": None}

    scores = [a["score"] / a["total_questions"] for a in attempts if a["total_questions"] > 0]
    return {
        "attempts": len(attempts),
        "best_score": round(max(scores) * 100, 1) if scores else 0,
        "avg_score": round(sum(scores) / len(scores) * 100, 1) if scores else 0,
        "last_attempt": attempts[0]["completed_at"]
    }


def batch_create_students(names: list, class_id: str) -> list:
    """Batch create students with auto-generated usernames and graphical passwords.

    Args:
        names: List of student full names
        class_id: The class ID to assign students to

    Returns:
        List of dicts with username, password, full_name, and status
    """
    # Get existing usernames to avoid duplicates
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    existing_names = set(row[0] for row in cursor.fetchall())
    conn.close()

    results = []

    for full_name in names:
        if not full_name or not full_name.strip():
            continue

        full_name = full_name.strip()

        # Generate unique username
        username = generate_username_from_name(full_name, list(existing_names))

        # Generate graphical password
        password = generate_graphical_password(1)

        # Create user
        if create_user(username, password, "student", full_name, class_id):
            existing_names.add(username)
            results.append({
                "full_name": full_name,
                "username": username,
                "password": password,
                "status": "success"
            })
        else:
            results.append({
                "full_name": full_name,
                "username": username,
                "password": password,
                "status": "failed"
            })

    return results


def regenerate_class_passwords(class_id: str) -> list:
    """Regenerate graphical passwords for all students in a class.

    Args:
        class_id: The class ID

    Returns:
        List of dicts with user_id, username, full_name, password, and status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all students in the class
    cursor.execute(
        "SELECT id, username, full_name FROM users WHERE class_id = ? AND role = 'student'",
        (class_id,)
    )
    students = cursor.fetchall()
    
    results = []
    for student in students:
        user_id = student[0]
        username = student[1]
        full_name = student[2] or username
        
        # Generate new password
        new_password = generate_graphical_password(1)
        
        # Update password in database
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        
        results.append({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "password": new_password,
            "status": "success"
        })
    
    conn.commit()
    conn.close()
    return results
