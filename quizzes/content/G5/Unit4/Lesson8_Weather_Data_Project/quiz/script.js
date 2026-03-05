const correctAnswers = {
    q1: 'A',
    q2: 'B',
    q3: 'B',
    q4: 'B',
    q5: 'B',
    q6: 'C',
    q7: 'B',
    q8: 'B'
};

const explanations = {
    q1: "Correct! The goal is to create a complete weather data management system.",
    q1_wrong: "Not quite. The project goal is to build a complete weather data system.",
    q2: "Correct! You need to collect at least 10 records of weather data.",
    q2_wrong: "Not quite. The project requires at least 10 records.",
    q3: "Correct! Your system should include 5 or more data fields.",
    q3_wrong: "Not quite. You need 5 or more fields like date, temp, rainfall, etc.",
    q4: "Correct! First, choose your scope - what data you will collect.",
    q4_wrong: "Not quite. Planning starts with choosing what data to collect.",
    q5: "Correct! You can use online services, school stations, or collect your own data.",
    q5_wrong: "Not quite. Data can come from many sources including online and manual collection.",
    q6: "Correct! Line charts show temperature changes over time.",
    q6_wrong: "Not quite. Line charts are best for showing changes over time.",
    q7: "Correct! Present your data, charts, and findings to the class.",
    q7_wrong: "Not quite. Your presentation should include data, charts, and what you learned.",
    q8: "Correct! The focus is on completeness, not perfection.",
    q8_wrong: "Not quite. Making it complete with all components is most important."
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
        alert('Please answer all questions before checking! 请先回答所有问题！');
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
    scoreText.textContent = `You got ${score} out of 8 correct! 你答对了 ${score}/8 题！`;

    let stars = '';
    let message = '';
    let messageClass = '';

    const percentage = score / 8;

    if (percentage === 1) {
        stars = '⭐⭐⭐⭐⭐';
        message = "AMAZING JOB! You're a Data System Expert! 你是数据系统专家！";
        messageClass = 'amazing';
    } else if (percentage >= 0.75) {
        stars = '⭐⭐⭐⭐';
        message = "GREAT WORK! You almost got them all! 做得很好！";
        messageClass = 'great';
    } else if (percentage >= 0.5) {
        stars = '⭐⭐⭐';
        message = "GOOD TRY! Review the answers and try again! 继续努力！";
        messageClass = 'good';
    } else if (percentage >= 0.25) {
        stars = '⭐⭐';
        message = "KEEP LEARNING! Let's review together! 继续学习！";
        messageClass = 'keep';
    } else {
        stars = '⭐';
        message = "LET'S REVIEW! Go back to the lesson! 回去看看课程吧！";
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
    console.log('🎉 G5 Weather Data System Project Quiz loaded!');
    console.log('Good luck, students! 祝学生们好运！');
});
