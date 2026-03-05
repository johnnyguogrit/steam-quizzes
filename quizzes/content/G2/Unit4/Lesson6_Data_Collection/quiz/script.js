// Correct answers for Lesson 6 Quiz
const correctAnswers = {
    1: 'B',  // |||| = 4 tally marks
    2: 'C',  // |||| with diagonal = 5
    3: 'B',  // Survey is asking questions to collect information
    4: 'B',  // Tally marks are for counting and recording data
    5: 'A'   // First step is prepare your survey sheet
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
