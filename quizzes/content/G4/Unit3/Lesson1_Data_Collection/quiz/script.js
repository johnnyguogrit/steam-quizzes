// Correct answers for Lesson 1 Quiz
const correctAnswers = {
    q1: 'B',
    q2: 'C',
    q3: 'B',
    q4: 'C',
    q5: 'A',
    q6: 'B',
    q7: 'B'
};

document.getElementById('quizForm').addEventListener('submit', function(e) {
    e.preventDefault();

    let score = 0;

    // Check answers for questions 1-7
    for (let i = 1; i <= 7; i++) {
        const questionName = 'q' + i;
        const selected = document.querySelector(`input[name="${questionName}"]:checked`);

        // Remove previous styling
        const options = document.querySelectorAll(`input[name="${questionName}"]`);
        options.forEach(option => {
            option.parentElement.classList.remove('correct', 'incorrect');
        });

        if (selected) {
            const userAnswer = selected.value;
            if (userAnswer === correctAnswers[questionName]) {
                score++;
                selected.parentElement.classList.add('correct');
            } else {
                selected.parentElement.classList.add('incorrect');
            }
        }
    }

    // Calculate percentage
    const percentage = Math.round((score / 7) * 100);

    // Display result
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('hidden');

    let message = '';
    let emoji = '';

    if (percentage >= 90) {
        emoji = '🌟';
        message = 'Excellent! / 优秀！';
    } else if (percentage >= 70) {
        emoji = '👍';
        message = 'Good job! / 做得好！';
    } else if (percentage >= 50) {
        emoji = '📚';
        message = 'Keep practicing! / 继续练习！';
    } else {
        emoji = '💪';
        message = 'Try again! / 再试一次！';
    }

    resultDiv.innerHTML = `
        <h2>${emoji} Quiz Results / 测验结果</h2>
        <p class="score-display">Your Score: ${score} out of 7 / 你的得分：7分中${score}分</p>
        <p class="percentage-display">Percentage: ${percentage}% / 百分比：${percentage}%</p>
        <p class="message">${message}</p>
        <button onclick="window.location.reload()" class="retry-btn">Try Again / 再试一次</button>
    `;

    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth' });
});
