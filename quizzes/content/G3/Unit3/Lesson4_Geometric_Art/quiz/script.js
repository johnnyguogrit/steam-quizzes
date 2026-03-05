// Correct answers for Lesson 4 Quiz
const correctAnswers = {
    q1: 'a',
    q2: 'b',
    q3: 'b',
    q4: 'b',
    q5: 'b',
    q6: 'b'
};

// Answer explanations
const explanations = {
    q1: 'The project requires using loops to create patterns. / 项目要求使用循环来创建图案。',
    q2: 'The Pen extension in Scratch allows you to draw and add colors. / Scratch中的画笔扩展允许你绘画和添加颜色。',
    q3: 'Planning helps you know what blocks and strategies to use for your art. / 计划帮助你了解为你的艺术使用什么积木和策略。',
    q4: 'A gallery walk is when students share and view each other\'s artwork. / 画廊展示是学生分享和观看彼此作品的时候。',
    q5: 'The Pen extension in Scratch allows you to draw and add colors. / Scratch中的画笔扩展允许你绘画和添加颜色。',
    q6: 'Planning first helps you create better art! / 先计划帮助你创作更好的艺术！'
};

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
                feedbackHTML += `<div class="feedback-item correct">✓ Question ${i} Correct! / 第${i}题正确！</div>`;
            } else {
                userAnswer.closest('.option').classList.add('incorrect');
                feedbackHTML += `<div class="feedback-item incorrect">✗ Question ${i} Incorrect. ${explanations[questionName]}</div>`;
            }
        } else {
            feedbackHTML += `<div class="feedback-item incorrect">✗ Question ${i} Not answered. ${explanations[questionName]}</div>`;
        }
    }
    
    // Show result
    const resultDiv = document.getElementById('result');
    const scorePara = resultDiv.querySelector('.score');
    const feedbackDiv = document.getElementById('feedback');
    
    const percentage = (score / total) * 100;
    let message = '';
    if (percentage === 100) {
        message = '🎉 Excellent! / 太棒了！';
    } else if (percentage >= 75) {
        message = '👍 Great job! / 做得好！';
    } else if (percentage >= 50) {
        message = '😊 Good try! Keep practicing! / 继续努力！';
    } else {
        message = '📚 Keep learning! You can do it! / 继续学习，你能行！';
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
