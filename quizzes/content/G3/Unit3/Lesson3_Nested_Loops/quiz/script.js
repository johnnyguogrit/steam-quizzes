// Correct answers for Lesson 3 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'b',
    q3: 'c',
    q4: 'b',
    q5: 'b',
    q6: 'b'
};

// Answer explanations
const explanations = {
    q1: 'A nested loop is a loop inside another loop. / 嵌套循环是一个循环在另一个循环里面。',
    q2: 'The inner loop runs first, completing all its repetitions before the outer loop continues. / 内层循环先运行，完成所有重复后外层循环继续。',
    q3: '5 × 3 = 15 total repetitions! / 5 × 3 = 15次总重复！',
    q4: 'The nested loop creates a pattern of triangles repeated multiple times. / 嵌套循环创建了一个重复多次的三角形图案。',
    q5: '4 × 3 = 12 total repetitions! / 4 × 3 = 12次总重复！',
    q6: 'The inner loop runs first, completing all its repetitions before the outer loop continues. / 内层循环先运行，完成所有重复后外层循环继续。'
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
