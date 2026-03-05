// Correct answers for Lesson 2: User Input and Output
const correctAnswers = {
    q1: 'A',  // Information going INTO the computer
    q2: 'B',  // Pressing a key on keyboard
    q3: 'C',  // Information coming OUT of the computer
    q4: 'B',  // Input
    q5: 'B',  // Showing "Correct!" or "Try again!"
    q6: 'B',  // Input -> Check -> Output
    q7: 'D',  // Shout at the computer
    q8: 'C'   // Green
};

const explanations = {
    q1: "Correct! INPUT is information going INTO the computer!",
    q1_wrong: "Not quite. INPUT is information going INTO the computer, like typing or clicking!",
    q2: "Correct! Pressing a key on the keyboard is an example of input!",
    q2_wrong: "Not quite. Keyboard presses are input. Screen text and sounds are output!",
    q3: "Correct! OUTPUT is information coming OUT of the computer!",
    q3_wrong: "Not quite. OUTPUT is information coming OUT, like sounds and screen text!",
    q4: "Correct! The player's answer choice is input going into the computer!",
    q4_wrong: "Not quite. The answer choice is input - it goes INTO the computer!",
    q5: "Correct! Showing feedback like 'Correct!' is output from the computer!",
    q5_wrong: "Not quite. Displaying messages is output. Clicking is input!",
    q6: "Correct! First input (answer), then check, then output (feedback)!",
    q6_wrong: "Not quite. The order is: Input -> Check -> Output!",
    q7: "Correct! Shouting at the computer is not a way to answer a quiz!",
    q7_wrong: "Not quite. You can click, press keys, or touch screens to answer!",
    q8: "Correct! Green usually shows a correct answer in quizzes!",
    q8_wrong: "Not quite. Green usually means correct. Red means incorrect!"
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
        message = "AMAZING JOB! You're an Input/Output Expert!";
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
    console.log('G5 User Input and Output Quiz loaded!');
    console.log('Good luck, students!');
});
