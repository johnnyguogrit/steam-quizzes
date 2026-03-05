# STEAM Quiz Platform - Technical Specification

## Project Overview

**Project Name**: STEAM Quiz Platform
**Version**: 1.4.0
**Repository**: https://github.com/johnnyguogrit/steam-quizzes
**Deployment**: https://steam-quizzes.streamlit.app
**Status**: Production ✅

---

## Table of Contents

1. [Architecture](#architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Quiz Structure](#quiz-structure)
7. [Deployment](#deployment)
8. [Future Enhancements](#future-enhancements)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit Cloud                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   app.py    │  │   auth.py   │  │ database.py │            │
│  │  (Entry)    │  │  (Login)    │  │  (SQLite)   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Pages (Multipage)                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │  │
│  │  │  Landing   │ │ Quiz View  │ │  Teacher   │          │  │
│  │  │            │ │            │ │ Dashboard  │          │  │
│  │  └────────────┘ └────────────┘ └────────────┘          │  │
│  │  ┌────────────┐                                         │  │
│  │  │ Student    │                                         │  │
│  │  │ Progress   │                                         │  │
│  │  └────────────┘                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Static Content                        │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │  quizzes/landing/ (Landing page HTML/CSS/JS)     │   │  │
│  │  │  quizzes/content/ (40 quiz folders)              │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend Framework** | Streamlit | ^1.28.0 |
| **Backend Language** | Python | 3.10+ |
| **Database** | SQLite | Built-in |
| **Data Processing** | pandas | ^2.0.0 |
| **Visualization** | plotly | ^5.17.0 |
| **Excel Export** | openpyxl | ^3.1.0 |
| **Static Content** | HTML/CSS/JavaScript | - |
| **Hosting** | Streamlit Cloud | - |
| **Version Control** | Git | - |

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
    full_name TEXT,
    class_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Classes Table
```sql
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    grade_level TEXT,
    teacher_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

### Quiz Attempts Table
```sql
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    score INTEGER,
    total_questions INTEGER,
    time_spent INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Quiz Versions Table
```sql
CREATE TABLE quiz_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id TEXT NOT NULL,
    version TEXT,
    content_hash TEXT,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Badges Table
```sql
CREATE TABLE badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_type TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, badge_type)
);
```

---

## API Reference

### Authentication (`auth.py`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `init_auth()` | - | None | Initialize session state |
| `login(username, password)` | str, str | bool | Authenticate user |
| `logout()` | - | None | Clear session state |
| `is_authenticated()` | - | bool | Check login status |
| `is_teacher()` | - | bool | Check if teacher role |
| `is_student()` | - | bool | Check if student role |

### Database (`database.py`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `init_db()` | - | None | Create all tables |
| `create_user(...)` | username, password, role, full_name, class_id | bool | Create new user |
| `authenticate_user(username, password)` | str, str | Dict\|None | Validate credentials |
| `record_quiz_attempt(...)` | user_id, quiz_id, score, total, time_spent | int | Save quiz result |
| `get_user_attempts(user_id)` | int | List[Dict] | Get all attempts |
| `get_class_statistics(class_id)` | str | Dict | Class analytics |
| `export_class_data(class_id)` | str | List[Dict] | Export data |

### Configuration (`config.py`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `get_all_quizzes()` | - | List[Dict] | All 40 quizzes |
| `get_quizzes_by_grade(grade)` | str (g1-g5) | List[Dict] | Filter by grade |
| `get_quiz_by_id(quiz_id)` | str | Dict\|None | Single quiz |
| `search_quizzes(query)` | str | List[Dict] | Search quizzes |

---

## User Roles & Permissions

### Teacher
| Permission | Description |
|------------|-------------|
| Create classes | ✅ |
| Add/remove students | ✅ |
| View all student progress | ✅ |
| View class statistics | ✅ |
| Export data (CSV/Excel) | ✅ |
| Take quizzes | ✅ |
| Delete users | ✅ (own students only) |

### Student
| Permission | Description |
|------------|-------------|
| Browse quizzes | ✅ |
| Take quizzes | ✅ |
| View own progress | ✅ |
| View own badges | ✅ |
| Export own history | ✅ |
| Create classes | ❌ |
| View other students | ❌ |

---

## Quiz Structure

### File Organization
```
quizzes/content/
├── G1/Unit3/Lesson1_Data_Collection/quiz/
│   ├── index.html    # Quiz content
│   ├── script.js     # Quiz logic
│   ├── styles.css    # Quiz styling
│   └── README.md     # Documentation
├── G1/Unit3/Lesson2_Algorithms_Food/quiz/
├── ... (40 quiz folders total)
```

### Quiz Metadata
```python
{
    "id": "g1-u3-l1",           # Unique identifier
    "grade": "g1",              # Grade level (g1-g5)
    "unit": "unit3",            # Unit (unit3/unit4)
    "lesson": 1,                # Lesson number
    "title": "Data Collection",
    "chinese": "数据收集",
    "path": "quizzes/content/G1/Unit3/Lesson1_Data_Collection/quiz/index.html",
    "questions": 4,             # Number of questions
    "description": "Learn about data!",
    "keywords": ["data", "collection"]
}
```

### Quiz Count by Grade
| Grade | Unit 3 | Unit 4 | Total |
|-------|--------|--------|-------|
| G1 | 4 quizzes | 4 quizzes | 8 |
| G2 | 4 quizzes | 4 quizzes | 8 |
| G3 | 4 quizzes | 4 quizzes | 8 |
| G4 | 4 quizzes | 4 quizzes | 8 |
| G5 | 4 quizzes | 4 quizzes | 8 |
| **Total** | **20** | **20** | **40** |

---

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app/app.py
```

### Streamlit Cloud Deployment
1. Connect GitHub repository
2. Set main file: `streamlit_app/app.py`
3. Auto-deploys on push to `main` branch

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| - | (None required) | - |

### Known Limitations
- **Data Persistence**: SQLite database resets on Streamlit Cloud redeploy
  - **Mitigation**: Regular data exports, backup before updates
- **Concurrent Users**: Limited by Streamlit's execution model
- **File Upload**: Not implemented (uses static content only)

---

## Badge System

| Badge | Requirement | Icon |
|-------|-------------|------|
| First Quiz | Complete any quiz | 🌟 |
| Perfect Score | 100% on any quiz | ⭐ |
| G1 Master | Complete all G1 quizzes | 🏆 |
| G2 Master | Complete all G2 quizzes | 🌱 |
| G3 Master | Complete all G3 quizzes | 🚀 |
| G4 Master | Complete all G4 quizzes | 💎 |
| G5 Master | Complete all G5 quizzes | 🥇 |

---

## Future Enhancements

### Phase 2 (Planned)
- [ ] External PostgreSQL database for persistent storage
- [ ] Password reset functionality
- [ ] Email notifications for teachers
- [ ] Parent access to student progress
- [ ] Quiz timer settings
- [ ] Randomized question order
- [ ] Question bank system

### Phase 3 (Considered)
- [ ] Multi-language support (full i18n)
- [ ] Mobile app version
- [ ] Offline mode capability
- [ ] Integration with LMS systems
- [ ] Advanced analytics dashboard
- [ ] Peer comparison (anonymized)
- [ ] AI-powered quiz recommendations

---

## Support

- **Documentation**: See [README.md](README.md)
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: https://github.com/johnnyguogrit/steam-quizzes/issues

---

**Last Updated**: 2026-03-05
**Maintainer**: johnnyguogrit

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.4.0 | 2026-03-05 | Add animal picture passwords (Code.org style) - 12 animals with SVG icons, emoji display, and bilingual names |
| v1.3.3 | 2026-03-05 | Fix SyntaxError caused by missing comma in import statement |
| v1.3.1 | 2026-03-05 | Fix password storage for PDF credentials (store in session state) |
| v1.3.0 | 2026-03-05 | Add PDF download for Class Credentials with Chinese and emoji support |
| v1.2.3 | 2026-03-05 | Fix Excel download 404 error with BytesIO |
| v1.2.2 | 2026-03-05 | Fix duplicate widget ID errors |
| v1.2.1 | 2026-03-05 | Fix indentation errors |
| v1.2.0 | 2026-03-05 | Simplify Teacher Dashboard UX, combined class creation with student import |
| v1.1.0 | 2026-03-05 | Add single emoji graphical passwords and batch import |
| v1.0.4 | 2026-03-05 | Improve delete class confirmation flow |
| v1.0.3 | 2026-03-05 | Add delete class functionality |
| v1.0.2 | 2026-03-05 | Fix quiz rendering with st.html() |
| v1.0.1 | 2026-03-05 | Fix quiz path calculation |
| v1.0.0 | 2026-03-05 | Initial release |
