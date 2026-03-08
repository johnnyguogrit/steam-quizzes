"""
Migration: Add class_code field to classes table
Run: python streamlit_app/migrations/add_class_code.py
"""
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from streamlit_app.database import get_connection, CLASS_CODE_WORDS

import random


def generate_unique_class_code():
    """Generate a unique 8-letter class code."""
    # Use get_class_by_code after import to avoid circular import
    from streamlit_app.database import get_class_by_code

    while True:
        code = random.choice(CLASS_CODE_WORDS)
        if not get_class_by_code(code):
            return code


def migrate():
    """Add class_code column and generate codes for existing classes."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if class_code column exists
    cursor.execute("PRAGMA table_info(classes)")
    columns = [col[1] for col in cursor.fetchall()]

    if "class_code" not in columns:
        print("Adding class_code column to classes table...")
        # SQLite can't add UNIQUE column to existing table
        cursor.execute("ALTER TABLE classes ADD COLUMN class_code TEXT")

        # Generate codes for existing classes
        cursor.execute("SELECT id, name FROM classes")
        existing = cursor.fetchall()

        print(f"Generating codes for {len(existing)} existing classes...")
        for cls_id, name in existing:
            code = generate_unique_class_code()
            cursor.execute("UPDATE classes SET class_code = ? WHERE id = ?", (code, cls_id))
            print(f"  Generated code '{code}' for class: {name}")

        conn.commit()
        print(f"\n[OK] Migration complete: Added codes to {len(existing)} classes")
    else:
        print("[INFO] class_code column already exists")

        # Check for any NULL class_code values and fill them
        cursor.execute("SELECT id, name FROM classes WHERE class_code IS NULL")
        null_codes = cursor.fetchall()

        if null_codes:
            print(f"Found {len(null_codes)} classes without class_code, generating...")
            for cls_id, name in null_codes:
                code = generate_unique_class_code()
                cursor.execute("UPDATE classes SET class_code = ? WHERE id = ?", (code, cls_id))
                print(f"  Generated code '{code}' for class: {name}")
            conn.commit()
            print(f"\n[OK] Updated {len(null_codes)} classes with class codes")
        else:
            print("[OK] All classes already have class codes")

    conn.close()


if __name__ == "__main__":
    migrate()
