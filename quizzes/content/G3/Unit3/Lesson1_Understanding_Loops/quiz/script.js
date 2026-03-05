// Correct answers for Lesson 1 Quiz
const correctAnswers = {
    q1: 'b',
    q2: 'd',
    q3: 'b',
    q4: 'a',
    q5: 'c',
    q6: 'b'
};

// Answer explanations
const explanations = {
    q1: 'A loop is a command that repeats actions in programming. / 循环是编程中重复执行动作的命令。',
    q2: 'Reading a book once is NOT a loop - it happens only one time! / 只读一次书不是循环，它只发生一次！',
    q3: 'Loops help us write less code and avoid mistakes. / 循环帮助我们写更少的代码，避免错误。',
    q4: '"REPEAT 4 times" means to do the action 4 times. / 意思是执行这个动作4次。',
    q5: 'Winning a race one time is NOT a loop because it only happens once! / 赢得一次比赛不是循环，因为它只发生一次！',
    q6: 'A hexagon has 6 sides, so you repeat 6 times. / 六边形有6条边，所以重复6次。'
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
