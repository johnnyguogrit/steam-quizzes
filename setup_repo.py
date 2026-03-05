"""
Script to initialize git repository and prepare for GitHub push
"""
import subprocess
import os
from pathlib import Path

# Change to project directory
os.chdir(r"D:\AIDevelop\ClaudeDev\steam\steam-quizzes")

print("=== STEAM Quiz Platform - GitHub Setup ===\n")

# Initialize git repo if not already initialized
if not Path(".git").exists():
    print("1. Initializing git repository...")
    subprocess.run(["git", "init"], check=True)
else:
    print("1. Git repository already exists.")

# Add all files
print("\n2. Adding files to git...")
subprocess.run(["git", "add", "."], check=True)

# Create initial commit
print("\n3. Creating initial commit...")
result = subprocess.run(
    ["git", "commit", "-m", "Initial commit: STEAM Quiz Platform"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("   ✓ Commit created successfully!")
else:
    print(f"   Note: {result.stderr.strip()}")

print("\n=== Next Steps ===")
print("""
To push to GitHub:

1. Create a new repository at https://github.com/new
   - Repository name: steam-quizzes
   - Make it Public (for Streamlit Cloud free tier)

2. Add the remote:
   git remote add origin https://github.com/johnnyguogrit/steam-quizzes.git

3. Push to GitHub:
   git branch -M main
   git push -u origin main

4. Deploy to Streamlit Cloud:
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your GitHub repo
   - Main file path: streamlit_app/app.py
   - Click "Deploy"
""")
