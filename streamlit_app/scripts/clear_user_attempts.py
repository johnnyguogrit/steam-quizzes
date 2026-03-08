"""
Clear quiz attempts for a specific user.
Run this on Streamlit Cloud to reset a user's progress.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from database import get_connection

def clear_user_attempts(username_or_full_name):
    """Clear all quiz attempts for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()

    # Find user
    cursor.execute('SELECT id, username, full_name FROM users WHERE username LIKE ? OR full_name LIKE ?',
                   (f'%{username_or_full_name}%', f'%{username_or_full_name}%'))
    users = cursor.fetchall()

    if not users:
        print(f"No users found matching '{username_or_full_name}'")
        return False

    # Show matching users
    print(f"Found {len(users)} matching user(s):")
    for user in users:
        user_id, username, full_name = user
        cursor.execute('SELECT COUNT(*) FROM quiz_attempts WHERE user_id=?', (user_id,))
        count = cursor.fetchone()[0]
        print(f"  - {full_name} ({username}) - ID: {user_id} - {count} attempts")

    # Clear attempts for all matching users
    total_deleted = 0
    for user in users:
        user_id = user[0]
        cursor.execute('DELETE FROM quiz_attempts WHERE user_id=?', (user_id,))
        deleted = cursor.rowcount
        total_deleted += deleted
        print(f"Deleted {deleted} attempts for {user[2]}")

    conn.commit()
    conn.close()

    print(f"\nTotal deleted: {total_deleted} quiz attempts")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clear quiz attempts for a user')
    parser.add_argument('user', help='Username or full name to search for')
    args = parser.parse_args()

    clear_user_attempts(args.user)
