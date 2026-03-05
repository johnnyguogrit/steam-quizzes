const correctAnswers = {
    q1: 'B',  // A code breaker is someone who solves secret codes
    q2: 'A',  // Looking for patterns is an important clue
    q3: 'D',  // Both A and B - teamwork is faster and people see different patterns
    q4: 'A',  // BCD with -1 shift = ABC
    q5: 'B'   // Working well with a team is the most important skill
};

function checkAnswers() {
    let score = 0;
    const totalQuestions = 5;

    for (let i = 1; i <= totalQuestions; i++) {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        const feedbackEl = document.getElementById(`feedback${i}`);
        const options = document.querySelectorAll(`input[name="q${i}"]`);
        const parentOptions = document.querySelectorAll(`.question:nth-of-type(${i}) .option`);

        // Reset all options
        parentOptions.forEach(opt => {
            opt.classList.remove('correct', 'incorrect', 'selected');
        });

        feedbackEl.classList.remove('show', 'correct', 'incorrect');

        if (selected) {
            const userAnswer = selected.value;
            const correctAnswer = correctAnswers[`q${i}`];

            // Mark selected option
            selected.closest('.option').classList.add('selected');

            if (userAnswer === correctAnswer) {
                score++;
                feedbackEl.textContent = '✅ Correct! 太棒了！';
                feedbackEl.classList.add('show', 'correct');
                selected.closest('.option').classList.add('correct');
            } else {
                feedbackEl.textContent = `❌ Incorrect. The answer is ${correctAnswer}. 答案是 ${correctAnswer}`;
                feedbackEl.classList.add('show', 'incorrect');
                selected.closest('.option').classList.add('incorrect');

                // Highlight correct answer
                parentOptions.forEach(opt => {
                    if (opt.querySelector('input').value === correctAnswer) {
                        opt.classList.add('correct');
                    }
                });
            }
        } else {
            feedbackEl.textContent = '⚠️ Please select an answer! 请选择一个答案！';
            feedbackEl.classList.add('show', 'incorrect');
        }
    }

    showResults(score, totalQuestions);
}

function showResults(score, total) {
    const resultsDiv = document.getElementById('results');
    const percentage = (score / total) * 100;

    let stars = '';
    let messageClass = '';
    let messageText = '';

    if (score === total) {
        stars = '⭐⭐⭐⭐⭐';
        messageClass = 'amazing';
        messageText = 'Amazing! You are a Master Code Breaker! 太棒了！你是解密大师！';
    } else if (percentage >= 75) {
        stars = '⭐⭐⭐⭐';
        messageClass = 'great';
        messageText = 'Great Work! Almost perfect! 做得好！几乎完美！';
    } else if (percentage >= 50) {
        stars = '⭐⭐⭐';
        messageClass = 'good';
        messageText = 'Good Try! Keep practicing! 继续加油！';
    } else if (percentage >= 25) {
        stars = '⭐⭐';
        messageClass = 'keep';
        messageText = 'Keep Learning! You can do it! 继续学习！';
    } else {
        stars = '⭐';
        messageClass = 'review';
        messageText = 'Let\'s Review! Try again! 再试一次！';
    }

    resultsDiv.innerHTML = `
        <div class="results">
            <h2>🎉 Quiz Complete! 测验完成！</h2>
            <div class="score-display">
                <p>Your Score: <strong>${score} / ${total}</strong></p>
                <p class="stars">${stars}</p>
            </div>
            <div class="message ${messageClass}">
                <p>${messageText}</p>
            </div>
        </div>
    `;
    resultsDiv.style.display = 'block';

    // Show retry button
    document.getElementById('retryBtn').style.display = 'inline-block';
}

function resetQuiz() {
    // Clear all selections
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.checked = false;
    });

    // Remove all feedback classes
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('correct', 'incorrect', 'selected');
    });

    document.querySelectorAll('.feedback').forEach(fb => {
        fb.classList.remove('show', 'correct', 'incorrect');
        fb.textContent = '';
    });

    // Hide results and retry button
    document.getElementById('results').style.display = 'none';
    document.getElementById('retryBtn').style.display = 'none';

    // Clear bonus answer
    document.getElementById('bonusAnswer').value = '';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add click handlers for options
document.addEventListener('DOMContentLoaded', function() {
    const options = document.querySelectorAll('.option');
    options.forEach(option => {
        option.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
            }
        });
    });
});
