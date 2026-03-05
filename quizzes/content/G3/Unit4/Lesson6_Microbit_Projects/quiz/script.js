// Correct answers for Lesson 6 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'a',
    q3: 'c',
    q4: 'b',
    q5: 'b',
    q6: 'a'
};

// Answer explanations
const explanations = {
    q1: 'The accelerometer is a sensor that detects movement, shaking, and tilt. / 加速度传感器是检测移动、摇晃和倾斜的传感器。',
    q2: 'A variable is like a box that stores information that can change. / 变量就像一个存储可以改变的信息的盒子。',
    q3: 'When you shake, the step counter adds 1 to the steps variable. / 当你摇晃时，计步器给steps变量加1。',
    q4: '"Set steps to 0" resets the counter back to zero. / "将steps设为0"将计数器重置为零。',
    q5: 'The "if" block checks a condition and does something only when the condition is true. / "如果"模块检查条件，只在条件为真时做某事。',
    q5_wrong: 'In programming, "IF" checks a condition before doing something. / 在编程中，"如果"在做某事之前检查条件。',
    q6: 'To count steps, the micro:bit needs to be on your body to detect movement! / 为了计步，micro:bit需要在身上以检测运动！',
    q6_wrong: 'The micro:bit must move with your body to count your steps correctly. / micro:bit必须与身体一起移动才能正确计步。'
};

// Bonus answer check
const bonusAnswers = ['conditional', 'condition', 'if then', 'if-then', 'logic'];

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
        const isBonusCorrect = bonusAnswers.some(ans => bonusVal.includes(ans));
        if (isBonusCorrect) {
            feedbackHTML += `<div class="feedback-item correct">Bonus Correct! It called "Conditional" or "If-Then" logic! / 额外问题正确！这叫做"条件"或"如果-那么"逻辑！</div>`;
        } else {
            feedbackHTML += `<div class="feedback-item incorrect">Bonus: The answer is "Conditional" - using IF/THEN to make decisions! / 答案是"条件" - 使用如果/那么来做决定！</div>`;
        }
    }

    // Show result
    const resultDiv = document.getElementById('result');
    const scorePara = resultDiv.querySelector('.score');
    const feedbackDiv = document.getElementById('feedback');

    const percentage = (score / total) * 100;
    let message = '';
    if (percentage === 100) {
        message = 'Perfect! You are a Step Counter Expert! / 完美！你是计步器专家！';
    } else if (percentage >= 75) {
        message = 'Great job! Keep counting! / 做得好！继续计数！';
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
