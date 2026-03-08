"""
Quiz Viewer Page
Displays the selected quiz and handles score submission.
"""

import streamlit as st
import os
import time
from auth import require_auth, logout_button
from config import get_quiz_by_id
from database import record_quiz_attempt, get_quiz_attempts_by_quiz

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

# Check if this is the first attempt
existing_attempts = get_quiz_attempts_by_quiz(st.session_state.user_id, quiz_id)
is_first_attempt = len(existing_attempts) == 0

# Quiz header
st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0;">{quiz['title']}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{quiz['chinese']}</p>
        <p style="margin: 10px 0 0 0; font-size: 0.9rem;">{quiz['description']}</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">📝 {quiz['questions']} Questions | Grade {quiz['grade'].upper()} - {quiz['unit'].replace('unit', 'Unit ').upper()}</p>
        {"<p style='margin: 5px 0 0 0; font-size: 0.8rem; color: #FFD700;'>⭐ First Attempt - This score will be recorded!</p>" if is_first_attempt else "<p style='margin: 5px 0 0 0; font-size: 0.8rem; color: #aaa;'>Practice Mode - Score not recorded</p>"}
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

# Inject score reporting - auto-save to localStorage and notify parent
injected_js = f"""
<script>
// Streamlit Quiz Integration
(function() {{
    window.quizId = "{quiz_id}";
    window.userId = {st.session_state.user_id};
    window.startTime = Date.now();
    window.quizCompleted = false;
    window.autoSaveEnabled = {str(is_first_attempt).lower()};  // Only auto-save on first attempt

    // Clear any old results when loading new quiz
    localStorage.removeItem('steam_quiz_result');

    // Function to send score to server and update UI
    window.reportScore = function(score, total) {{
        if (window.quizCompleted) return;
        window.quizCompleted = true;

        const timeSpent = Math.round((Date.now() - window.startTime) / 1000);
        const percentage = Math.round((score / total) * 100);

        // Update the results display
        const resultsDiv = document.getElementById('streamlit-quiz-results');
        if (resultsDiv) {{
            const saveMsg = window.autoSaveEnabled ?
                '<p style="color: #4CAF50; font-weight: bold;">✅ Score automatically saved!</p>' :
                '<p style="color: #999;">Practice mode - score not recorded</p>';

            resultsDiv.innerHTML = `
                <div style="padding: 20px; background: #e8f5e9; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #4caf50;">🎉 Quiz Completed!</h2>
                    <p style="font-size: 1.2rem;"><strong>Score: ${{score}}/${{total}} (${{percentage}}%)</strong></p>
                    <p>Time spent: ${{timeSpent}} seconds</p>
                    ${{saveMsg}}
                </div>
            `;
        }}

        // Store result in localStorage with timestamp for auto-save polling
        const result = {{
            type: 'quiz_completed',
            quizId: "{quiz_id}",
            userId: {st.session_state.user_id},
            score: score,
            total: total,
            timeSpent: timeSpent,
            timestamp: Date.now(),
            autoSave: window.autoSaveEnabled
        }};

        try {{
            localStorage.setItem('steam_quiz_result', JSON.stringify(result));
            console.log('Result stored to localStorage:', result);

            // Trigger a custom event for the auto-save poller
            window.dispatchEvent(new CustomEvent('quizCompleted', {{ detail: result }}));
        }} catch (e) {{
            console.error('Error storing quiz result:', e);
        }}

        console.log('Quiz completed:', {{ score, total, timeSpent, autoSave: window.autoSaveEnabled }});
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

# Auto-save polling section - runs continuously to detect completed quizzes
st.markdown("---")

# Auto-save indicator
if is_first_attempt:
    st.info("🔄 **Auto-save enabled**: Your first attempt score will be automatically saved when you complete the quiz.")
else:
    st.info("📝 **Practice mode**: You've already taken this quiz. This attempt won't be recorded.")

# Auto-save polling using st.js()
if is_first_attempt:
    # Placeholder for auto-save status
    if 'auto_save_status' not in st.session_state:
        st.session_state.auto_save_status = {}

    # Check for quiz completion using st.js()
    try:
        result = st.js("""
            const resultStr = localStorage.getItem('steam_quiz_result');
            if (resultStr) {
                const result = JSON.parse(resultStr);
                const age = Date.now() - (result.timestamp || 0);
                if (age < 60000) {  // Valid for 1 minute
                    localStorage.removeItem('steam_quiz_result');
                    return result;
                }
            }
            return null;
        """)

        if result:
            # Create unique attempt key to prevent duplicate processing
            attempt_key = f"{quiz_id}_{result.get('timestamp', '')}"

            if not st.session_state.auto_save_status.get(attempt_key):
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
                    🎉 **First Attempt Saved!**
                    - Score: {result['score']}/{result['total']} ({percentage}%)
                    - Time: {result.get('timeSpent', 0)} seconds

                    Your result has been automatically saved!
                """)
                st.balloons()

                # Mark as processed
                st.session_state.auto_save_status[attempt_key] = True

    except AttributeError:
        # st.js() not available - show info for manual check
        st.info("💡 Complete the quiz and your result will be visible in 'My Progress'.")

# Instructions
st.markdown("""
### Instructions
1. Answer all questions by selecting the best option
2. Click "Check Answers" when you're done
3. Your score is automatically saved (first attempt only)
4. Check "My Progress" to see your statistics
""")
