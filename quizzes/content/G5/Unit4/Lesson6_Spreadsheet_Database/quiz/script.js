const correctAnswers = {
    q1: 'B',
    q2: 'B',
    q3: 'C',
    q4: 'A',
    q5: 'C',
    q6: 'A',
    q7: 'B',
    q8: 'C'
};

const explanations = {
    q1: "Correct! Each box in a spreadsheet is called a cell.",
    q1_wrong: "Not quite. Each box in a spreadsheet is called a cell.",
    q2: "Correct! Columns are labeled with letters (A, B, C...).",
    q2_wrong: "Not quite. Columns use letters, while rows use numbers.",
    q3: "Correct! Sort arranges data in a specific order.",
    q3_wrong: "Not quite. Sort organizes data in order, like A-Z or high to low.",
    q4: "Correct! Filter shows only the data you want to see.",
    q4_wrong: "Not quite. Filter hides data temporarily but doesn't delete it.",
    q5: "Correct! =AVERAGE(B2:B10) calculates the average.",
    q5_wrong: "Not quite. The AVERAGE formula calculates the mean value.",
    q6: "Correct! =MAX(B2:B10) finds the highest value.",
    q6_wrong: "Not quite. MAX finds the maximum/highest value.",
    q7: "Correct! The colon means 'through' or 'to' (from B2 to B10).",
    q7_wrong: "Not quite. B2:B10 means from cell B2 through cell B10.",
    q8: "Correct! The first row is the header row containing field names.",
    q8_wrong: "Not quite. The first row always contains headers (field names)."
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
        message = "AMAZING JOB! You're a Spreadsheet Expert! 你是电子表格专家！";
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
    console.log('🎉 G5 Spreadsheet Database Functions Quiz loaded!');
    console.log('Good luck, students! 祝学生们好运！');
});
