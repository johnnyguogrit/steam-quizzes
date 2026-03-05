# STEAM Quiz Landing Page

A colorful, interactive landing page for accessing all 40 STEAM quizzes across Grades 1-5.

## Features

- **Grade Tabs**: Switch between G1-G5 with colorful tabs
- **Unit Grouping**: Quizzes organized by unit (Unit 3: Programming Loops, Unit 4: Physical Computing)
- **Search Functionality**: Search by keyword, grade, unit, or lesson name
- **Unit Filter**: Filter quizzes by unit
- **Playful Design**: Colorful, engaging design for young students
- **New Window**: Quizzes open in new browser windows
- **Responsive**: Works on tablets and desktops

## File Structure

```
quiz-landing/
├── index.html       # Main HTML structure
├── styles.css       # Playful, colorful styling
├── script.js        # Interactive functionality
├── quiz-data.js     # All 40 quiz metadata
└── README.md        # This file
```

## Usage

1. Open `index.html` in a web browser
2. Select a grade using the colorful tabs at the top
3. Browse quizzes organized by unit
4. Click "Start Quiz" to open a quiz in a new window
5. Use the search bar to find specific quizzes

## Quiz Data

Each quiz includes:
- Title (English and Chinese)
- Description (English and Chinese)
- Path to quiz folder
- Number of questions (G1: 4, G2: 5, G3: 6, G4: 7, G5: 8)
- Keywords for search
- Grade, unit, and lesson identifiers

### Question Count by Grade

| Grade | Questions per Quiz | Total Quizzes |
|-------|-------------------|---------------|
| G1    | 4                 | 8             |
| G2    | 5                 | 8             |
| G3    | 6                 | 8             |
| G4    | 7                 | 8             |
| G5    | 8                 | 8             |

## Color Scheme

Each grade has its own color theme:
- **G1**: Pink (`#FF6B9D`)
- **G2**: Green (`#4CAF50`)
- **G3**: Purple (`#9C27B0`)
- **G4**: Blue (`#2196F3`)
- **G5**: Gold/Orange (`#FF9800`)

## Keyboard Shortcuts

- `Ctrl/Cmd + K`: Focus search bar

## Browser Compatibility

Works in all modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Adding New Quizzes

To add a new quiz, edit `quiz-data.js` and add to the appropriate grade/unit array:

```javascript
{
    id: 'g1-u3-l9',           // Unique identifier
    grade: 'g1',              // Grade level
    unit: 'unit3',            // Unit
    lesson: 9,                // Lesson number
    title: 'New Quiz Title',
    chinese: '中文标题',
    path: 'G1/Unit3/Lesson9_New/quiz/index.html',
    questions: 4,             // Number of questions
    description: 'Quiz description.',
    chineseDesc: '中文描述',
    keywords: ['keyword1', 'keyword2']
}
```

## Customization

### Changing Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --g1-primary: #FF6B9D;
    --g2-primary: #4CAF50;
    /* etc... */
}
```

### Modifying the Layout

- Grid columns: Edit `.quiz-grid` in `styles.css`
- Card size: Adjust `minmax(320px, 1fr)` in the grid template

---

**Spring 2026 STEAM Program** | Created with heart for young learners! 💚
