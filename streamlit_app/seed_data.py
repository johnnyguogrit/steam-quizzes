"""
Seed Data for STEAM Quiz Platform
Contains initial data for admin and G1A class.
Run this script to populate the database with seed data.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    get_connection, create_user, hash_password,
    create_class, init_db
)


def seed_database():
    """Seed the database with initial data."""
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT * FROM users WHERE username = 'SteamMaster'")
    if cursor.fetchone():
        print("Admin user already exists. Skipping seed.")
        conn.close()
        return

    # Create admin teacher
    admin_password = "steam2026"  # Change this to your desired password
    if create_user("SteamMaster", admin_password, "teacher", "Admin"):
        print("✓ Created admin user: SteamMaster")

        # Get admin ID
        cursor.execute("SELECT id FROM users WHERE username = 'SteamMaster'")
        admin_id = cursor.fetchone()[0]

        # Create G1A class
        try:
            # Import generate_unique_class_code
            from database import generate_unique_class_code

            class_code = generate_unique_class_code()

            cursor.execute(
                "INSERT INTO classes (name, grade_level, teacher_id, class_code) VALUES (?, ?, ?, ?)",
                ("G1A", "G1", admin_id, class_code)
            )
            conn.commit()
            class_id = cursor.lastrowid
            print(f"✓ Created class: G1A with code: {class_code}")

            # Create students for G1A
            students = [
                ("Zoey Shao", 2),
                ("Hailey He", 2),
                ("Mango Yu", 3),
                ("Jayden Lu", 4),
                ("Sean Zhou", 5),
                ("Candy Tang", 6),
                ("Lara Sun", 3),
                ("Bobby Ju", 7),
                ("Matthew Zeng", 7),
                ("Lion Lin", 7),
                ("Aria Fan", 3),
                ("Hailey Xiang", 2),
                ("Rock Luo", 5),
                ("Emma Cai", 3),
                ("Eason Xue", 6),
                ("Henry Deng", 3),
                ("Arjuna Zou", 4),
                ("Ray Ma", 8),
            ]

            for full_name, animal_num in students:
                from database import generate_username_from_name
                from database import get_all_users

                existing = [u['username'] for u in get_all_users()]
                username = generate_username_from_name(full_name, existing)

                if create_user(username, str(animal_num), "student", full_name, str(class_id)):
                    print(f"  ✓ Created student: {full_name} (username: {username}, password: {animal_num})")

            print(f"\n✓ Created {len(students)} students for G1A class")
            print(f"\n📋 Class Login Information:")
            print(f"   Class Code: {class_code}")
            print(f"   Admin Login: SteamMaster / {admin_password}")

        except Exception as e:
            print(f"Error creating class: {e}")
            conn.rollback()
    else:
        print("Failed to create admin user")

    conn.close()
    print("\n✅ Database seeding complete!")


if __name__ == "__main__":
    seed_database()
