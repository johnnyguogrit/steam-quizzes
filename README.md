# STEAM Quiz Platform 🎓

A comprehensive quiz platform for STEAM education, built with Streamlit. Teachers can create classes, assign quizzes, and track student progress.

## Features

- 🎯 **40 Interactive Quizzes** covering Grades 1-5, Units 3-4
- 👨‍🏫 **Teacher Dashboard** - Manage classes and view statistics
- 👨‍🎓 **Student Progress Tracking** - View attempts, scores, and badges
- 🏆 **Gamification** - Earn badges for achievements
- 📊 **Analytics** - Class and individual performance insights
- 📤 **Data Export** - Export results to CSV/Excel

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnnyguogrit/steam-quizzes.git
   cd steam-quizzes
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy quiz content**
   ```bash
   # Copy all quiz files from Spring_Term/LessonPlan to quizzes/content/
   # Maintain the directory structure
   ```

4. **Run the app**
   ```bash
   streamlit run streamlit_app/app.py
   ```

5. **Open in browser**
   ```
   http://localhost:8501
   ```

## Project Structure

```
steam-quizzes/
├── streamlit_app/          # Main application
│   ├── app.py              # Entry point with authentication
│   ├── auth.py             # Authentication logic
│   ├── database.py         # SQLite operations
│   ├── config.py           # Quiz metadata and config
│   └── pages/
│       ├── 1_Landing.py    # Quiz selection page
│       ├── 2_Quiz_View.py  # Quiz iframe viewer
│       ├── 3_Teacher_Dashboard.py  # Teacher management
│       └── 4_Student_Progress.py   # Student progress
├── quizzes/                # Quiz content
│   ├── landing/            # Landing page assets
│   └── content/            # All quiz HTML files
├── data/                   # Database and data files
├── requirements.txt        # Python dependencies
└── .streamlit/             # Streamlit config
```

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Connect your GitHub repository
5. Set main file path to `streamlit_app/app.py`
6. Click "Deploy"

### Environment Variables (Optional)

For production, consider using external database:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: For session encryption

## First Time Setup

### Creating Admin Account

1. Run the app locally
2. Go to "First Time Setup" tab
3. Enter admin credentials
4. Log in with the new account

### Creating Classes and Students

1. Log in as a teacher
2. Go to Teacher Dashboard
3. Navigate to "Create" tab
4. Create a class
5. Add students with usernames and passwords

## Quiz Content

The platform includes 40 quizzes organized by:

- **Grade 1**: Data Collection (Unit 3) + Dance Algorithms (Unit 4)
- **Grade 2**: Secret Codes (Unit 3) + Spreadsheets (Unit 4)
- **Grade 3**: Loops (Unit 3) + Physical Computing (Unit 4)
- **Grade 4**: Data Analysis (Unit 3) + Networks (Unit 4)
- **Grade 5**: Quiz App Development (Unit 3) + Data Systems (Unit 4)

Each quiz is designed with:
- Age-appropriate questions
- Bilingual support (English/Chinese)
- Immediate feedback
- Progress tracking

## User Roles

### Teacher
- Create and manage classes
- Add student accounts
- View class statistics
- Export data to CSV/Excel
- Track individual student progress

### Student
- Browse and complete quizzes
- View personal progress
- Earn badges for achievements
- Retake quizzes to improve scores

## Data Storage

- **Development**: SQLite database (`data/users.db`)
- **Production**: Recommended to use PostgreSQL or cloud database

**Note**: Streamlit Community Cloud has filesystem limitations. Database resets on redeploy. Consider:
- External database (Supabase, PostgreSQL)
- Regular data exports for backup

## Badge System

Students can earn:
- 🌟 **First Quiz** - Complete first quiz
- ⭐ **Perfect Score** - Get 100% on any quiz
- 🏆 **Grade Master** - Complete all quizzes in a grade

## Development

### Adding New Quizzes

1. Add quiz HTML files to `quizzes/content/`
2. Update `streamlit_app/config.py` with quiz metadata
3. Follow the existing quiz structure

### Customization

- **Colors**: Edit `.streamlit/config.toml`
- **Questions**: Modify HTML files in `quizzes/content/`
- **Database Schema**: Edit `streamlit_app/database.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.

---

**Spring 2026 STEAM Program** | Created with ❤️ for young learners
