// Correct answers for Lesson 8 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'd',
    q3: 'b',
    q4: 'b',
    q5: 'a',
    q6: 'd'
};

// Answer explanations
const explanations = {
    q1: 'Planning is the first step - think about what you want to make before coding! / 规划是第一步 - 在编码之前想想你想做什么！',
    q2: 'Writing a book is not a physical computing project option. / 写书不是物理计算项目选项。',
    q3: 'Good designers think about the USER - is it easy to understand and use? / 优秀的设计师考虑用户 - 容易理解和使用吗？',
    q4: 'Peer testing means swapping with partners and trying each other projects. / 同伴测试意味着与伙伴交换并尝试彼此的项目。',
    q5: 'Start with the main feature first and get it working before adding more! / 从主要功能开始，首先让它工作，然后再添加更多！',
    q5_wrong: 'It\'s best to build step by step - start simple, get it working, then add more. / 最好逐步构建 - 从简单开始，让它工作，然后再添加更多。',
    q6: 'Sharing what was challenging shows your learning journey and problem-solving! / 分享什么具有挑战性展示了你的学习过程和解决问题的能力！',
    q6_wrong: 'Talking about challenges shows how you worked through problems to create your project. / 谈论挑战表明你如何通过解决问题来创建项目。'
};

// Bonus answer check
const bonusAnswers = ['showcase', 'expo', 'exhibition', 'presentation', 'project showcase'];

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
            feedbackHTML += `<div class="feedback-item correct">Bonus Correct! It called a Project Showcase or Expo! / 额外问题正确！这叫做项目展示或博览会！</div>`;
        } else {
            feedbackHTML += `<div class="feedback-item incorrect">Bonus: The answer is "Showcase" or "Expo" - where you display your work! / 答案是"展示"或"博览会" - 你展示作品的地方！</div>`;
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
        message = 'Great job! You are ready to create! / 做得好！你准备好创作了！';
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
