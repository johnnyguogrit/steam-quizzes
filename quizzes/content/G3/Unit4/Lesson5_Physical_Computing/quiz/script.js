// Correct answers for Lesson 5 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'c',
    q3: 'a',
    q4: 'b',
    q5: 'b',
    q6: 'a'
};

// Answer explanations
const explanations = {
    q1: 'Physical computing is building interactive systems that can sense and respond to the real world. / 物理计算是构建可以感知和响应现实世界的交互系统。',
    q2: 'The micro:bit has 25 red LED lights arranged in a 5x5 grid. / micro:bit有25个排列成5x5网格的红色LED灯。',
    q3: 'Pressing buttons is an INPUT - it tells the micro:bit what to do. / 按下按钮是输入 - 它告诉micro:bit要做什么。',
    q4: 'We use makecode.microbit.org to program the micro:bit. / 我们使用makecode.microbit.org来编程micro:bit。',
    q5: 'The simulator in MakeCode works like a real micro:bit, so you can test without a device! / MakeCode中的模拟器像真实的micro:bit一样工作，所以你可以在没有设备的情况下测试！',
    q5_wrong: 'The simulator lets you test your code before downloading to a real micro:bit. / 模拟器让你在下载到真实micro:bit之前测试代码。',
    q6: 'Debugging means finding and fixing mistakes in your code - it\'s an important skill! / 调试意味着找到并修复代码中的错误 - 这是一项重要技能！',
    q6_wrong: 'Debugging is how programmers find and fix errors in their code. / 调试是程序员在代码中查找和修复错误的方法。'
};

// Bonus answer check
const bonusAnswers = ['accelerometer', 'accelerometer sensor', 'acceleration sensor', 'motion sensor'];

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
            feedbackHTML += `<div class="feedback-item correct">Bonus Correct! The accelerometer detects movement! / 额外问题正确！加速度传感器检测运动！</div>`;
        } else {
            feedbackHTML += `<div class="feedback-item incorrect">Bonus: The answer is "accelerometer" - it detects shaking and movement! / 答案是"加速度传感器" - 它检测摇晃和运动！</div>`;
        }
    }

    // Show result
    const resultDiv = document.getElementById('result');
    const scorePara = resultDiv.querySelector('.score');
    const feedbackDiv = document.getElementById('feedback');

    const percentage = (score / total) * 100;
    let message = '';
    if (percentage === 100) {
        message = 'Perfect! You are a Physical Computing Expert! / 完美！你是物理计算专家！';
    } else if (percentage >= 75) {
        message = 'Great job! Keep learning! / 做得好！继续学习！';
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
