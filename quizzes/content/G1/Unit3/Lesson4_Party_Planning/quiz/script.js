const correctAnswers = {
    q1: 'correct',
    q2: 'correct',
    q3: 'correct',
    q4: 'correct',
};

const explanations = {
    q1: "🎉 Correct! We use the data from our class survey to decide what food to buy!",
    q1_wrong: "🤔 Not quite. We should use the data we collected from asking our classmates!",
    q2: "🎉 Correct! 20 students × 2 slices each = 40 slices of pizza!",
    q2_wrong: "🤔 Not quite. Multiply: 20 students × 2 slices = 40 slices total!",
    q3: "🎉 Correct! Every invitation needs to tell WHEN, WHERE, and WHAT (theme)!",
    q3_wrong: "🤔 Not quite. Invitations need to say when, where, and what the party is about!",
    q4: "🎉 Correct! We have a limited budget, so we need to plan carefully!",
    q4_wrong: "🤔 Not quite. We need to think about budget because we only have a certain amount of money!",
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

    for (let i = 1; i <= 4; i++) {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        const feedback = document.getElementById(`feedback${i}`);

        if (!selected) {
            allAnswered = false;
            continue;
        }

        const isCorrect = selected.value === 'correct';

        const allOptions = document.querySelectorAll(`input[name="q${i}"]`);
        allOptions.forEach(opt => {
            const label = opt.closest('.option');
            label.classList.remove('correct', 'incorrect');
            if (opt.value === 'correct') {
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
        alert('Please answer all questions before checking! 📝');
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
    scoreText.textContent = `You got ${score} out of 4 correct!`;

    let stars = '';
    let message = '';
    let messageClass = '';

    const percentage = score / 4;

    if (percentage === 1) {
        stars = '⭐⭐⭐⭐⭐';
        message = "AMAZING JOB! You're a Party Planning Expert! 🏆";
        messageClass = 'amazing';
    } else if (percentage >= 0.75) {
        stars = '⭐⭐⭐⭐';
        message = "GREAT WORK! You almost got them all! 💪";
        messageClass = 'great';
    } else if (percentage >= 0.5) {
        stars = '⭐⭐⭐';
        message = "GOOD TRY! Review the answers and try again! 📚";
        messageClass = 'good';
    } else if (percentage >= 0.25) {
        stars = '⭐⭐';
        message = "KEEP LEARNING! Let's review together! 🌱";
        messageClass = 'keep';
    } else {
        stars = '⭐';
        message = "LET'S REVIEW! Go back to the lesson! 💡";
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
    console.log('🎉 G1 Party Planning Quiz loaded!');
    console.log('Good luck, students! 📚');
});
