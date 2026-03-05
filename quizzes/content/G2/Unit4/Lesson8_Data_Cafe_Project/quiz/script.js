// Correct answers for Lesson 8 Quiz
const correctAnswers = {
    1: 'B',  // Data Cafe is about designing menu and collecting data
    2: 'B',  // Menu has food and drink items with prices
    3: 'B',  // Present menu and data to class
    4: 'B',  // Use spreadsheet to organize data
    5: 'B'   // Prices should be reasonable
};

let score = 0;
let answered = {};

function selectAnswer(questionNum, answer) {
    // Don't allow re-answering
    if (answered[questionNum]) {
        return;
    }

    answered[questionNum] = true;
    const feedback = document.getElementById(`feedback${questionNum}`);
    const questionDiv = document.getElementById(`q${questionNum}`);
    const buttons = questionDiv.querySelectorAll('.option-btn');

    // Disable all buttons
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.cursor = 'not-allowed';
    });

    // Check if answer is correct
    if (answer === correctAnswers[questionNum]) {
        score++;
        document.getElementById('currentScore').textContent = score;
        feedback.className = 'feedback correct';
        feedback.innerHTML = '<span class="emoji">✅</span> Correct! / 正确！';
        event.target.className += ' correct-answer';
    } else {
        feedback.className = 'feedback incorrect';
        feedback.innerHTML = `<span class="emoji">❌</span> Not quite. The answer is ${correctAnswers[questionNum]}.<br>不太对。答案是 ${correctAnswers[questionNum]}`;
        event.target.className += ' wrong-answer';
        // Highlight the correct answer
        buttons.forEach(btn => {
            if (btn.onclick.toString().includes(`'${correctAnswers[questionNum]}'`)) {
                btn.className += ' correct-answer';
            }
        });
    }
}

function resetQuiz() {
    score = 0;
    answered = {};
    document.getElementById('currentScore').textContent = '0';

    for (let i = 1; i <= 5; i++) {
        const questionDiv = document.getElementById(`q${i}`);
        const buttons = questionDiv.querySelectorAll('.option-btn');
        const feedback = document.getElementById(`feedback${i}`);

        buttons.forEach(btn => {
            btn.disabled = false;
            btn.style.cursor = 'pointer';
            btn.className = 'option-btn';
        });

        feedback.className = 'feedback';
        feedback.innerHTML = '';
    }
}
