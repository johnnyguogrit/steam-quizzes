const correctAnswers = {
    q1: 'A',
    q2: 'C',
    q3: 'C',
    q4: 'B',
    q5: 'A',
    q6: 'C',
    q7: 'B',
    q8: 'A'
};

const explanations = {
    q1: "Correct! Data visualization means making pictures to help us understand data.",
    q1_wrong: "Not quite. Data visualization is turning numbers into pictures we can understand.",
    q2: "Correct! Bar charts are best for comparing different categories or groups.",
    q2_wrong: "Not quite. Bar charts are the best choice for comparing categories.",
    q3: "Correct! Line charts show changes and trends over time.",
    q3_wrong: "Not quite. Line charts are specifically designed to show changes over time.",
    q4: "Correct! Pie charts show parts of a whole, like percentages.",
    q4_wrong: "Not quite. Pie charts show how something is divided into parts.",
    q5: "Correct! First you select the data you want to chart.",
    q5_wrong: "Not quite. You must select your data first before creating a chart.",
    q6: "Correct! Clear titles and labels help people understand what the chart shows.",
    q6_wrong: "Not quite. Labels and titles are essential for understanding charts.",
    q7: "Correct! Bar charts are great for comparing rainfall across different cities.",
    q7_wrong: "Not quite. Bar charts work best for comparing categories like cities.",
    q8: "Correct! Line charts show temperature changes over the week.",
    q8_wrong: "Not quite. Line charts are best for showing temperature changes over time."
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
        message = "AMAZING JOB! You're a Visualization Expert! 你是可视化专家！";
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
    console.log('🎉 G5 Data Analysis and Visualization Quiz loaded!');
    console.log('Good luck, students! 祝学生们好运！');
});
