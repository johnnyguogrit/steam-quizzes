"""
Quiz Viewer Page
Displays the selected quiz and handles score submission.
"""

import streamlit as st
import os
import json
from auth import require_auth, logout_button
from config import get_quiz_by_id
from database import record_quiz_attempt

# Page config
st.set_page_config(
    page_title="Quiz View",
    page_icon="📝",
    layout="wide"
)

require_auth()

# Sidebar
with st.sidebar:
    st.title("🎓 Quiz View")
    st.markdown(f"👤 {st.session_state.full_name or st.session_state.user_name}")
    st.markdown("---")
    logout_button()

    if st.button("← Back to Quizzes", use_container_width=True):
        st.switch_page("pages/1_Landing.py")

    if st.button("📈 My Progress", use_container_width=True):
        st.switch_page("pages/4_Student_Progress.py")

# Get quiz ID from session state
quiz_id = st.session_state.get("selected_quiz")

if not quiz_id:
    st.warning("No quiz selected. Please choose a quiz from the landing page.")
    if st.button("Go to Quiz Selection", use_container_width=True):
        st.switch_page("pages/1_Landing.py")
    st.stop()

quiz = get_quiz_by_id(quiz_id)

if not quiz:
    st.error(f"Quiz not found: {quiz_id}")
    if st.button("Back to Quizzes", use_container_width=True):
        st.switch_page("pages/1_Landing.py")
    st.stop()

# Quiz header
st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0;">{quiz['title']}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{quiz['chinese']}</p>
        <p style="margin: 10px 0 0 0; font-size: 0.9rem;">{quiz['description']}</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">📝 {quiz['questions']} Questions | Grade {quiz['grade'].upper()} - {quiz['unit'].replace('unit', 'Unit ').upper()}</p>
    </div>
""", unsafe_allow_html=True)

# Get the quiz file path
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(current_dir))
quiz_path = os.path.join(base_dir, quiz['path'])

# Check if quiz file exists
if not os.path.exists(quiz_path):
    st.error(f"""
        ### Quiz file not found

        The quiz file could not be located at:
        `{quiz_path}`

        Please make sure all quiz content has been copied to the `quizzes/content/` directory.
    """)
    st.info("""
        **To set up the quizzes:**
        1. Copy all quiz directories from `Spring_Term/LessonPlan/` to `steam-quizzes/quizzes/content/`
        2. Maintain the same directory structure
        3. Restart the Streamlit app
    """)
    st.stop()

# Read the original HTML
with open(quiz_path, 'r', encoding='utf-8') as f:
    quiz_html = f.read()

# Get the CSS file path for styling
css_path = os.path.join(os.path.dirname(quiz_path), 'styles.css')
quiz_css = ""
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        quiz_css = f.read()

# Get the JS file path
js_path = os.path.join(os.path.dirname(quiz_path), 'script.js')
quiz_js = ""
if os.path.exists(js_path):
    with open(js_path, 'r', encoding='utf-8') as f:
        quiz_js = f.read()

# Inject score reporting - store result in localStorage
injected_js = f"""
<script>
// Streamlit Quiz Integration
(function() {{
    window.quizId = "{quiz_id}";
    window.userId = {st.session_state.user_id};
    window.startTime = Date.now();
    window.quizCompleted = false;

    // Clear any old results when loading new quiz
    localStorage.removeItem('steam_quiz_result');

    // Function to send score to Streamlit
    window.reportScore = function(score, total) {{
        if (window.quizCompleted) return;
        window.quizCompleted = true;

        const timeSpent = Math.round((Date.now() - window.startTime) / 1000);
        const percentage = Math.round((score / total) * 100);

        // Update the results display
        const resultsDiv = document.getElementById('streamlit-quiz-results');
        if (resultsDiv) {{
            resultsDiv.innerHTML = `
                <div style="padding: 20px; background: #e8f5e9; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #4caf50;">🎉 Quiz Completed!</h2>
                    <p style="font-size: 1.2rem;"><strong>Score: ${{score}}/${{total}} (${{percentage}}%)</strong></p>
                    <p>Time spent: ${{timeSpent}} seconds</p>
                    <p style="color: #666;">Click the button below to save your result!</p>
                </div>
            `;
        }}

        // Store result in localStorage with timestamp
        const result = {{
            type: 'quiz_completed',
            quizId: "{quiz_id}",
            userId: {st.session_state.user_id},
            score: score,
            total: total,
            timeSpent: timeSpent,
            timestamp: Date.now()
        }};

        try {{
            localStorage.setItem('steam_quiz_result', JSON.stringify(result));
            console.log('Result stored to localStorage:', result);
        }} catch (e) {{
            console.error('Error storing quiz result:', e);
        }}

        console.log('Quiz completed:', {{ score, total, timeSpent }});
    }};

    // Override checkAnswers function - MUST be loaded AFTER quiz JS
    const originalCheckAnswers = window.checkAnswers;
    if (typeof originalCheckAnswers === 'function') {{
        window.checkAnswers = function() {{
            const result = originalCheckAnswers.apply(this, arguments);

            // Wait for results to be calculated, then extract score
            setTimeout(() => {{
                let score = 0;
                let total = {quiz['questions']};

                // Try to get score from DOM
                const scoreText = document.querySelector('#scoreText')?.textContent ||
                                  document.querySelector('.score')?.textContent ||
                                  document.querySelector('[id*="score"]')?.textContent;

                if (scoreText) {{
                    const match = scoreText.match(/(\\d+)\\s*out of\\s*(\\d+)/);
                    if (match) {{
                        score = parseInt(match[1]);
                        total = parseInt(match[2]);
                    }}
                }}

                // Count correct answers if no score found
                if (score === 0) {{
                    const correctOptions = document.querySelectorAll('.option.correct');
                    const selectedCorrect = document.querySelectorAll('.option.correct.selected');
                    if (correctOptions.length > 0) {{
                        score = selectedCorrect.length;
                        total = correctOptions.length;
                    }}
                }}

                window.reportScore(score, total);
            }}, 300);

            return result;
        }};
    }}

    // Watch for results div to appear
    const observer = new MutationObserver((mutations) => {{
        mutations.forEach((mutation) => {{
            mutation.addedNodes.forEach((node) => {{
                if (node.id === 'results' || node.classList?.contains('results')) {{
                    setTimeout(() => {{
                        let score = 0;
                        let total = {quiz['questions']};

                        const scoreText = node.querySelector('#scoreText')?.textContent ||
                                        node.querySelector('.score')?.textContent;

                        if (scoreText) {{
                            const match = scoreText.match(/(\\d+)\\s*out of\\s*(\\d+)/);
                            if (match) {{
                                score = parseInt(match[1]);
                                total = parseInt(match[2]);
                            }}
                        }}

                        window.reportScore(score, total);
                    }}, 200);
                }}
            }});
        }});
    }});

    observer.observe(document.body, {{ childList: true, subtree: true }});
}})();
</script>

<!-- Container for results -->
<div id="streamlit-quiz-results"></div>
"""

# Insert CSS if available
if quiz_css:
    quiz_html = quiz_html.replace('</head>', f'<style>{quiz_css}</style></head>')

# IMPORTANT: Insert quiz JS FIRST, then our injected JS AFTER
# This ensures our override of checkAnswers works correctly
scripts_to_insert = ''
if quiz_js:
    scripts_to_insert += f'<script>{quiz_js}</script>'
scripts_to_insert += injected_js

if '</body>' in quiz_html:
    quiz_html = quiz_html.replace('</body>', scripts_to_insert + '</body>')
else:
    quiz_html = quiz_html.replace('</html>', scripts_to_insert + '</html>')

# Display the quiz using st.html (Streamlit 1.31+)
try:
    st.html(quiz_html, height=800)
except Exception as e:
    # Fallback to components.v1.html for older Streamlit versions
    st.components.v1.html(quiz_html, height=800, scrolling=True)

# Save Result Button Section
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.info("### After finishing the quiz:")
    st.markdown("1. Click **Check Answers** in the quiz above")
    st.markdown("2. Your score will appear automatically")
    st.markdown("3. Click the button below to save your result")

    if st.button("✅ Save My Quiz Result", type="primary", key="save_quiz_result"):
        # Try to use st.js() if available (Streamlit 1.33+)
        try:
            result = st.js("""
                const resultStr = localStorage.getItem('steam_quiz_result');
                if (resultStr) {
                    const result = JSON.parse(resultStr);
                    const age = Date.now() - (result.timestamp || 0);
                    if (age < 300000) {
                        localStorage.removeItem('steam_quiz_result');
                        return result;
                    }
                }
                return null;
            """)

            if result:
                # Initialize quiz tracking in session state if not exists
                if 'quiz_last_processed' not in st.session_state:
                    st.session_state.quiz_last_processed = {}

                # Create unique attempt key to prevent duplicate processing
                attempt_key = f"{quiz_id}_{result.get('timestamp', '')}"

                if not st.session_state.quiz_last_processed.get(attempt_key):
                    # Record the quiz attempt
                    record_quiz_attempt(
                        st.session_state.user_id,
                        result['quizId'],
                        result['score'],
                        result['total'],
                        result.get('timeSpent', 0)
                    )

                    percentage = round(result['score'] / result['total'] * 100)

                    st.success(f"""
                        🎉 **Quiz Completed!**
                        - Score: {result['score']}/{result['total']} ({percentage}%)
                        - Time: {result.get('timeSpent', 0)} seconds

                        Your result has been saved to the database!
                    """)
                    st.balloons()

                    # Mark as processed
                    st.session_state.quiz_last_processed[attempt_key] = True

                    # Add a button to view progress
                    if st.button("📈 View My Progress", key="goto_progress_after_save"):
                        st.switch_page("pages/4_Student_Progress.py")
            else:
                st.warning("""
                    No quiz result found! Please make sure you:
                    1. ✅ Answered all questions
                    2. ✅ Clicked "Check Answers" in the quiz
                    3. ✅ See your score displayed in the quiz

                    Then click "Save My Quiz Result" again.
                """)

        except AttributeError:
            # st.js() not available - use manual result entry
            st.warning("""
            **Automatic saving not available in your Streamlit version.**

            Please enter your score manually:
            """)

            col_a, col_b = st.columns(2)
            with col_a:
                manual_score = st.number_input("Your Score", min_value=0, max_value=quiz['questions'], value=0, step=1)
            with col_b:
                st.write(f"out of {quiz['questions']} questions")

            if st.button("Save Manual Result", type="secondary"):
                # Initialize quiz tracking in session state if not exists
                if 'quiz_last_processed' not in st.session_state:
                    st.session_state.quiz_last_processed = {}

                attempt_key = f"{quiz_id}_manual_{int(datetime.now().timestamp())}"

                # Record the quiz attempt
                record_quiz_attempt(
                    st.session_state.user_id,
                    quiz_id,
                    manual_score,
                    quiz['questions'],
                    0  # No time data for manual entry
                )

                percentage = round(manual_score / quiz['questions'] * 100)

                st.success(f"""
                    🎉 **Quiz Result Saved!**
                    - Score: {manual_score}/{quiz['questions']} ({percentage}%)

                    Your result has been saved!
                """)
                st.balloons()
                st.session_state.quiz_last_processed[attempt_key] = True

# Instructions
st.markdown("""
---
### Instructions
1. Answer all questions by selecting the best option
2. Click "Check Answers" when you're done
3. Click "Save My Quiz Result" to save your score
4. Check "My Progress" to see your updated statistics
""")
