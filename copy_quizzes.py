"""
Script to copy quiz content from LessonPlan to steam-quizzes
"""
import shutil
import os
from pathlib import Path

# Source and destination paths
source_base = Path(r"D:\AIDevelop\ClaudeDev\steam\Spring_Term\LessonPlan")
dest_base = Path(r"D:\AIDevelop\ClaudeDev\steam\steam-quizzes\quizzes\content")

# Grade and unit combinations
grades = ["G1", "G2", "G3", "G4", "G5"]
units = ["Unit3", "Unit4"]

# Copy all quiz directories
copied_count = 0
for grade in grades:
    for unit in units:
        source_dir = source_base / grade / unit
        if not source_dir.exists():
            continue

        # Find all quiz directories
        for lesson_dir in source_dir.iterdir():
            quiz_dir = lesson_dir / "quiz"
            if quiz_dir.exists():
                # Create destination directory
                dest_dir = dest_base / grade / unit / lesson_dir.name / "quiz"
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Copy all files
                for file in quiz_dir.iterdir():
                    if file.is_file():
                        shutil.copy2(file, dest_dir / file.name)
                        copied_count += 1
                        print(f"Copied: {file}")

print(f"\nTotal files copied: {copied_count}")
print("Done!")
