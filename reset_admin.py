"""
Admin Password Reset Script
Run this to reset or create an admin account
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from database import get_user_by_username, create_user, update_user_password, hash_password, get_connection

def reset_admin_password(username="SteamMaster", new_password=None):
    """Reset admin password or create new admin account."""

    if new_password is None:
        new_password = "admin123"  # Default password

    print("=== Admin Password Reset ===")
    print(f"Username: {username}")
    print(f"New Password: {new_password}")
    print()

    # Check if user exists
    user = get_user_by_username(username)

    if user:
        # Update existing user
        print(f"[OK] User '{username}' found (ID: {user['id']})")
        if update_user_password(user['id'], new_password):
            print(f"[OK] Password updated successfully!")
        else:
            print(f"[ERROR] Failed to update password")
    else:
        # Create new user
        print(f"[WARN] User '{username}' not found")
        print("Creating new admin account...")
        if create_user(username, new_password, "teacher", "Admin"):
            print(f"[OK] Admin account created successfully!")
        else:
            print(f"[ERROR] Failed to create admin account (username may already exist)")

    print()
    print("=== Login Credentials ===")
    print(f"Username: {username}")
    print(f"Password: {new_password}")
    print()
    print("You can now login at: http://localhost:8501")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reset or create admin account")
    parser.add_argument("--username", default="SteamMaster", help="Admin username")
    parser.add_argument("--password", default="admin123", help="New password")

    args = parser.parse_args()

    reset_admin_password(args.username, args.password)
