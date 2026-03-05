// Correct answers for Lesson 5 Quiz - Network Basics
const correctAnswers = {
    q1: 'A',
    q2: 'B',
    q3: 'C',
    q4: 'B',
    q5: 'B',
    q6: 'C',
    q7: 'B'
};

document.getElementById('quizForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    let score = 0;
    const totalQuestions = 7;
    
    // Loop through questions 1 to 7
    for (let i = 1; i <= totalQuestions; i++) {
        const questionName = 'q' + i;
        const selectedAnswer = document.querySelector(`input[name="${questionName}"]:checked`);
        
        if (selectedAnswer) {
            const userAnswer = selectedAnswer.value;
            if (userAnswer === correctAnswers[questionName]) {
                score++;
            }
        }
    }
    
    const percentage = Math.round((score / totalQuestions) * 100);
    
    // Display result
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('hidden');
    
    let resultClass = 'needs-work';
    let message = '';
    
    if (percentage === 100) {
        resultClass = 'perfect';
        message = 'Excellent! You are a Network Expert! | 太棒了！你是网络专家！';
    } else if (percentage >= 80) {
        resultClass = 'good';
        message = 'Great job! You understand networks well! | 做得好！你很了解网络！';
    } else if (percentage >= 60) {
        resultClass = 'good';
        message = 'Good effort! Keep learning about networks! | 继续努力！继续学习网络知识！';
    } else {
        resultClass = 'needs-work';
        message = 'Keep practicing! Review the lesson and try again! | 继续练习！复习课程后再试一次！';
    }
    
    resultDiv.className = 'result ' + resultClass;
    resultDiv.innerHTML = `
        <h2>Quiz Complete!</h2>
        <h2>测验完成！</h2>
        <p class="score">Your score: ${score} out of ${totalQuestions}</p>
        <p class="score">你的分数：${totalQuestions}分中得${score}分</p>
        <p class="percentage">${percentage}%</p>
        <p class="message">${message}</p>
    `;
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth' });
});
