// STEAM Quiz Landing Page - Interactive Script
(function() {
    'use strict';

    // State
    let currentGrade = 'g1';
    let searchQuery = '';

    // DOM Elements
    const quizGrid = document.getElementById('quizGrid');
    const searchInput = document.getElementById('searchInput');
    const gradeTabs = document.querySelectorAll('.grade-tab');
    const noResults = document.getElementById('noResults');

    // Grade names for display
    const gradeNames = {
        g1: 'Grade 1',
        g2: 'Grade 2',
        g3: 'Grade 3',
        g4: 'Grade 4',
        g5: 'Grade 5'
    };

    // Unit names for display
    const unitNames = {
        unit3: 'Unit 3',
        unit4: 'Unit 4'
    };

    // Unit themes for styling
    const unitThemes = {
        unit3: { emoji: '🎯', bg: '#FFE0B2', border: '#FF9800' },
        unit4: { emoji: '⚡', bg: '#C8E6C9', border: '#4CAF50' }
    };

    // Helper: Get all quizzes as a flat array
    function getAllQuizzes() {
        const allQuizzes = [];
        const grades = ['g1', 'g2', 'g3', 'g4', 'g5'];
        const units = ['unit3', 'unit4'];

        grades.forEach(grade => {
            units.forEach(unit => {
                if (quizData[grade] && quizData[grade][unit]) {
                    quizData[grade][unit].forEach(quiz => {
                        allQuizzes.push(quiz);
                    });
                }
            });
        });

        return allQuizzes;
    }

    // Helper: Get quizzes by grade
    function getQuizzesByGrade(grade) {
        const quizzes = [];
        const units = ['unit3', 'unit4'];

        units.forEach(unit => {
            if (quizData[grade] && quizData[grade][unit]) {
                quizData[grade][unit].forEach(quiz => {
                    quizzes.push(quiz);
                });
            }
        });

        return quizzes;
    }

    // Render a single quiz card
    function createQuizCard(quiz) {
        const card = document.createElement('article');
        card.className = `quiz-card ${quiz.grade}`;
        card.setAttribute('data-id', quiz.id);
        card.setAttribute('data-unit', quiz.unit);
        card.setAttribute('data-grade', quiz.grade);

        // Determine emoji based on grade
        const gradeEmojis = {
            g1: '🌟',
            g2: '🌱',
            g3: '🚀',
            g4: '💎',
            g5: '🏆'
        };

        const unitEmojis = {
            unit3: '🎯',
            unit4: '⚡'
        };

        card.innerHTML = `
            <div class="quiz-header">
                <span class="quiz-lesson">Lesson ${quiz.lesson}</span>
                <span class="quiz-badge">${gradeEmojis[quiz.grade]} ${quiz.questions} Questions</span>
            </div>
            <h3 class="quiz-title">${quiz.title}</h3>
            <p class="quiz-description">${quiz.description}</p>
            <div class="quiz-meta">
                <span class="quiz-meta-item">
                    <span class="icon">${unitEmojis[quiz.unit]} ${unitNames[quiz.unit]}</span>
                </span>
                <span class="quiz-meta-item">
                    <span class="icon">📝</span>
                    <span>${quiz.questions} questions</span>
                </span>
            </div>
            <a href="${quiz.path}" class="quiz-button" target="_blank" rel="noopener">
                Start Quiz! ${gradeEmojis[quiz.grade]}
            </a>
        `;

        return card;
    }

    // Render unit header
    function createUnitHeader(unit) {
        const header = document.createElement('div');
        header.className = `unit-header ${unit}`;
        header.style.background = unitThemes[unit].bg;
        header.style.borderLeftColor = unitThemes[unit].border;

        header.innerHTML = `
            <h2>${unitThemes[unit].emoji} ${unitNames[unit]}</h2>
        `;

        return header;
    }

    // Render quizzes grouped by unit
    function renderQuizzes(quizzes) {
        quizGrid.innerHTML = '';

        if (quizzes.length === 0) {
            noResults.style.display = 'block';
            return;
        }

        noResults.style.display = 'none';

        // Group by unit
        const grouped = {};
        quizzes.forEach(quiz => {
            if (!grouped[quiz.unit]) {
                grouped[quiz.unit] = [];
            }
            grouped[quiz.unit].push(quiz);
        });

        // Render units in order (Unit 3 first, then Unit 4)
        ['unit3', 'unit4'].forEach(unit => {
            if (grouped[unit] && grouped[unit].length > 0) {
                // Add unit header
                quizGrid.appendChild(createUnitHeader(unit));

                // Add quiz cards for this unit
                grouped[unit].forEach(quiz => {
                    quizGrid.appendChild(createQuizCard(quiz));
                });
            }
        });
    }

    // Filter and render based on current state
    function applyFilters() {
        let quizzes = getQuizzesByGrade(currentGrade);

        // Apply search filter
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            quizzes = quizzes.filter(quiz => {
                const titleMatch = quiz.title.toLowerCase().includes(query);
                const descMatch = quiz.description.toLowerCase().includes(query);
                const keywordMatch = quiz.keywords.some(k => k.toLowerCase().includes(query));
                const lessonMatch = `lesson ${quiz.lesson}`.includes(query);
                const unitMatch = quiz.unit.includes(query);
                const gradeMatch = quiz.grade.includes(query) || gradeNames[quiz.grade].toLowerCase().includes(query);

                return titleMatch || descMatch || keywordMatch || lessonMatch || unitMatch || gradeMatch;
            });
        }

        renderQuizzes(quizzes);
    }

    // Grade tab click handler
    function handleGradeClick(e) {
        const clickedTab = e.target.closest('.grade-tab');
        if (!clickedTab) return;

        // Remove active class from all tabs
        gradeTabs.forEach(tab => tab.classList.remove('active'));
        clickedTab.classList.add('active');

        // Update current grade
        currentGrade = clickedTab.getAttribute('data-grade');

        // Re-render
        applyFilters();

        // Add animation class
        quizGrid.classList.add('animating');
        setTimeout(() => quizGrid.classList.remove('animating'), 300);
    }

    // Search input handler
    function handleSearchInput(e) {
        searchQuery = e.target.value.trim();
        applyFilters();
    }

    // Initialize
    function init() {
        // Render initial quizzes (G1 by default)
        applyFilters();

        // Event listeners
        gradeTabs.forEach(tab => {
            tab.addEventListener('click', handleGradeClick);
        });

        searchInput.addEventListener('input', handleSearchInput);

        // Keyboard shortcut for search (Ctrl/Cmd + K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });

        // Add loading animation
        document.body.classList.add('loaded');

        console.log('🎮 STEAM Quiz Landing Page loaded!');
        console.log(`📚 Total quizzes available: ${getAllQuizzes().length} (8 per grade)`);
        console.log('🌟 G1: Unit 3 (Data) + Unit 4 (Dance) | 🌱 G2: Unit 3 (Codes) + Unit 4 (Spreadsheets)');
        console.log('🚀 G3: Unit 3 (Loops) + Unit 4 (Physical Computing) | 💎 G4: Unit 3 (Analysis) + Unit 4 (Networks) | 🏆 G5: Unit 3 (Quiz App) + Unit 4 (Data Systems)');
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
