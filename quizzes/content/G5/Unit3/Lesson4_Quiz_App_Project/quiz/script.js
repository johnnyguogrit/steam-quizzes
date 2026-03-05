// Correct answers for Lesson 4: Quiz App Project
const correctAnswers = {
    q1: 'A',  // Choose your topic
    q2: 'C',  // 10 questions
    q3: 'A',  // They should be about ONE topic
    q4: 'B',  // Multiple choice (A, B, C, D)
    q5: 'A',  // To find bugs and fix problems
    q6: 'B',  // Clear instructions
    q7: 'B',  // Having classmates test your quiz
    q8: 'B'   // Compliments and suggestions
};

const explanations = {
    q1: "Correct! The first step is choosing a topic you know well!",
    q1_wrong: "Not quite. The first step is choosing your quiz topic!",
    q2: "Correct! Your quiz should have at least 10 questions!",
    q2_wrong: "Not quite. The project requires at least 10 questions!",
    q3: "Correct! All quiz questions should be about the same topic!",
    q3_wrong: "Not quite. Good quizzes focus on ONE specific topic!",
    q4: "Correct! Multiple choice answers work best for quiz apps!",
    q4_wrong: "Not quite. Multiple choice is the best format for quiz apps!",
    q5: "Correct! Testing helps you find bugs and fix problems!",
    q5_wrong: "Not quite. Testing is important for finding and fixing bugs!",
    q6: "Correct! Clear instructions help players understand your quiz!",
    q6_wrong: "Not quite. Good quizzes need clear instructions for players!",
    q7: "Correct! Peer testing is when classmates test your quiz!",
    q7_wrong: "Not quite. Peer testing means having classmates try your quiz!",
    q8: "Correct! Good feedback includes both compliments and helpful suggestions!",
    q8_wrong: "Not quite. Good feedback balances compliments and suggestions!"
};

let answeredQuestions = new Set();

function highlightSelectedOption(questionNum) {
    const options = document.querySelectorAll(`input[name="q${questionNum}"]`);
    options.forEach(option => {
        const label = option.closest('.option');
        label.classList.remove('selected');
        if (option.checked) {
            label.classList.add('selected');
        }
    });
}

document.querySelectorAll('input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const questionNum = this.name.replace('q', '');
        highlightSelectedOption(questionNum);
    });
});

function checkAnswers() {
    let score = 0;
    let allAnswered = true;

    for (let i = 1; i <= 8; i++) {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        const feedback = document.getElementById(`feedback${i}`);

        if (!selected) {
            allAnswered = false;
            continue;
        }

        const isCorrect = selected.value === correctAnswers[`q${i}`];

        const allOptions = document.querySelectorAll(`input[name="q${i}"]`);
        allOptions.forEach(opt => {
            const label = opt.closest('.option');
            label.classList.remove('correct', 'incorrect');
            if (opt.value === correctAnswers[`q${i}`]) {
                label.classList.add('correct');
            } else if (opt.checked && !isCorrect) {
                label.classList.add('incorrect');
            }
        });

        feedback.className = 'feedback show';
        if (isCorrect) {
            score++;
            feedback.textContent = explanations[`q${i}`];
            feedback.classList.add('correct');
        } else {
            feedback.textContent = explanations[`q${i}_wrong`];
            feedback.classList.add('incorrect');
        }

        const allInputs = document.querySelectorAll(`input[name="q${i}"]`);
        allInputs.forEach(input => input.disabled = true);
    }

    if (!allAnswered) {
        alert('Please answer all questions before checking!');
        return;
    }

    showResults(score);
}

function showResults(score) {
    const resultsDiv = document.getElementById('results');
    const scoreText = document.getElementById('scoreText');
    const starsDisplay = document.getElementById('starsDisplay');
    const finalMessage = document.getElementById('finalMessage');
    const retryBtn = document.getElementById('retryBtn');

    resultsDiv.style.display = 'block';
    scoreText.textContent = `You got ${score} out of 8 correct!`;

    let stars = '';
    let message = '';
    let messageClass = '';

    const percentage = score / 8;

    if (percentage === 1) {
        stars = '⭐⭐⭐⭐⭐';
        message = "AMAZING JOB! You're a Quiz App Project Expert!";
        messageClass = 'amazing';
    } else if (percentage >= 0.75) {
        stars = '⭐⭐⭐⭐';
        message = "GREAT WORK! You almost got them all!";
        messageClass = 'great';
    } else if (percentage >= 0.5) {
        stars = '⭐⭐⭐';
        message = "GOOD TRY! Review the answers and try again!";
        messageClass = 'good';
    } else if (percentage >= 0.25) {
        stars = '⭐⭐';
        message = "KEEP LEARNING! Let's review together!";
        messageClass = 'keep';
    } else {
        stars = '⭐';
        message = "LET'S REVIEW! Go back to the lesson!";
        messageClass = 'review';
    }

    starsDisplay.textContent = stars;
    finalMessage.textContent = message;
    finalMessage.className = `message ${messageClass}`;
    retryBtn.style.display = 'inline-block';

    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function resetQuiz() {
    document.querySelectorAll('input[type="radio"]').forEach(input => {
        input.disabled = false;
        input.checked = false;
    });

    document.querySelectorAll('.option').forEach(label => {
        label.classList.remove('selected', 'correct', 'incorrect');
    });

    document.querySelectorAll('.feedback').forEach(feedback => {
        feedback.className = 'feedback';
        feedback.textContent = '';
    });

    document.getElementById('results').style.display = 'none';
    document.getElementById('retryBtn').style.display = 'none';
    document.getElementById('bonusAnswer').value = '';

    answeredQuestions.clear();

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('G5 Quiz App Project Quiz loaded!');
    console.log('Good luck, students!');
});
