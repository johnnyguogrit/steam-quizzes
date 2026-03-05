// Correct answers for Lesson 7 Quiz
const correctAnswers = {
    q1: 'c',
    q2: 'a',
    q3: 'b',
    q4: 'a',
    q5: 'c',
    q6: 'd'
};

// Answer explanations
const explanations = {
    q1: 'The micro:bit has 5 sensors: buttons A and B, accelerometer, light sensor, temperature sensor, and touch logo. / micro:bit有5个传感器：按钮A和B、加速度、光线、温度和触摸标志。',
    q2: 'The light sensor is hidden inside the LED matrix - the LEDs can both display AND sense light! / 光线传感器隐藏在LED矩阵内 - LED既可以显示也可以感知光线！',
    q3: 'The touch logo is the gold logo on the back of the micro:bit that works like a button. / 触摸标志是micro:bit背面金色标志，像按钮一样工作。',
    q4: 'The temperature sensor measures how hot or cold the micro:bit itself is. / 温度传感器测量micro:bit本身有多热或多冷。',
    q5: 'The light sensor returns 255 when it is very bright - that\'s the maximum value! / 光线传感器在非常亮时返回255 - 这是最大值！',
    q5_wrong: 'The light scale goes from 0 (dark) to 255 (bright). 255 is the highest number. / 光线刻度从0（暗）到255（亮）。255是最高数字。',
    q6: 'You can combine any sensors creatively to make interesting projects! / 你可以创意地组合任何传感器来制作有趣的项目！',
    q6_wrong: 'All sensor combinations can work well depending on your project idea. / 所有传感器组合都可以很好地工作，取决于你的项目想法。'
};

// Bonus answer check
const bonusAnswers = ['0', 'zero'];

document.getElementById('quizForm').addEventListener('submit', function(e) {
    e.preventDefault();

    let score = 0;
    let total = 6;
    let feedbackHTML = '';

    // Check each answer
    for (let i = 1; i <= total; i++) {
        const questionName = 'q' + i;
        const userAnswer = document.querySelector(`input[name="${questionName}"]:checked`);
        const correctAnswer = correctAnswers[questionName];

        const questionDiv = document.querySelector(`input[name="${questionName}"]`).closest('.question');
        const options = questionDiv.querySelectorAll('.option');

        // Reset styles
        options.forEach(opt => opt.classList.remove('correct', 'incorrect'));

        if (userAnswer) {
            if (userAnswer.value === correctAnswer) {
                score++;
                userAnswer.closest('.option').classList.add('correct');
                feedbackHTML += `<div class="feedback-item correct">Question ${i} Correct! / 第${i}题正确！</div>`;
            } else {
                userAnswer.closest('.option').classList.add('incorrect');
                const explanation = explanations[questionName] || explanations[questionName + '_wrong'] || '';
                feedbackHTML += `<div class="feedback-item incorrect">Question ${i} Incorrect. ${explanation}</div>`;
            }
        } else {
            const explanation = explanations[questionName] || explanations[questionName + '_wrong'] || '';
            feedbackHTML += `<div class="feedback-item incorrect">Question ${i} Not answered. ${explanation}</div>`;
        }
    }

    // Check bonus answer
    const bonusInput = document.querySelector('input[name="bonus"]');
    if (bonusInput && bonusInput.value.trim().toLowerCase()) {
        const bonusVal = bonusInput.value.trim().toLowerCase();
        const isBonusCorrect = bonusAnswers.some(ans => bonusVal === ans);
        if (isBonusCorrect) {
            feedbackHTML += `<div class="feedback-item correct">Bonus Correct! The light sensor returns 0 in darkness! / 额外问题正确！光线传感器在黑暗中返回0！</div>`;
        } else {
            feedbackHTML += `<div class="feedback-item incorrect">Bonus: The answer is 0 - the light sensor returns 0 when very dark! / 答案是0 - 光线传感器在非常暗时返回0！</div>`;
        }
    }

    // Show result
    const resultDiv = document.getElementById('result');
    const scorePara = resultDiv.querySelector('.score');
    const feedbackDiv = document.getElementById('feedback');

    const percentage = (score / total) * 100;
    let message = '';
    if (percentage === 100) {
        message = 'Perfect! You are a Sensors Expert! / 完美！你是传感器专家！';
    } else if (percentage >= 75) {
        message = 'Great job! Keep sensing! / 做得好！继续感知！';
    } else if (percentage >= 50) {
        message = 'Good effort! Review the lesson again. / 不错的努力！再复习一下课程。';
    } else {
        message = 'Keep practicing! You can do it! / 继续练习！你能行的！';
    }

    scorePara.innerHTML = `${message}<br>Your score / 你的分数: ${score}/${total} (${percentage}%)`;
    feedbackDiv.innerHTML = feedbackHTML;
    resultDiv.classList.remove('hidden');

    // Disable form inputs
    document.querySelectorAll('input[type="radio"]').forEach(input => {
        input.disabled = true;
    });
    document.querySelector('.submit-btn').style.display = 'none';

    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth' });
});
