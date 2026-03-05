// Correct answers for Lesson 2 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'a',
    q3: 'b',
    q4: 'c',
    q5: 'b',
    q6: 'b'
};

// Answer explanations
const explanations = {
    q1: 'Repeat blocks are in the CONTROL category, which is ORANGE in Scratch. / 重复积木在控制类别中，在Scratch中是橙色的。',
    q2: 'Motion blocks are BLUE in Scratch. / 运动积木在Scratch中是蓝色的。',
    q3: 'A square has 4 sides, so repeat 4 times. 360 ÷ 4 = 90 degrees. / 正方形有4条边，所以重复4次。360 ÷ 4 = 90度。',
    q4: 'The formula is 360 divided by the number of sides. / 公式是360除以边数。',
    q5: 'Motion blocks are BLUE in Scratch. / 运动积木在Scratch中是蓝色的。',
    q6: 'A triangle has 3 sides. 360 ÷ 3 = 120 degrees. / 三角形有3条边。360 ÷ 3 = 120度。'
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
