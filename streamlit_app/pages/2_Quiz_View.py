"""
Quiz Viewer Page
Displays the selected quiz and handles score submission.
"""

import streamlit as st
import os
import json
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

# Inject score reporting - store result in a hidden div that can be read by st.js()
injected_js = f"""
<script>
// Streamlit Quiz Integration
(function() {{
    window.quizId = "{quiz_id}";
    window.userId = {st.session_state.user_id};
    window.startTime = Date.now();
    window.quizCompleted = false;

    // Clear any old results
    localStorage.removeItem('steam_quiz_result');

    // Function to send score via postMessage to parent window
    window.reportScore = function(score, total) {{
        if (window.quizCompleted) return;
        window.quizCompleted = true;

        const timeSpent = Math.round((Date.now() - window.startTime) / 1000);
        const percentage = Math.round((score / total) * 100);

        // Create result object
        const result = {{
            type: 'quiz_completed',
            quizId: "{quiz_id}",
            userId: {st.session_state.user_id},
            score: score,
            total: total,
            timeSpent: timeSpent,
            timestamp: Date.now()
        }};

        // Store in localStorage (for debugging)
        try {{
            localStorage.setItem('steam_quiz_result', JSON.stringify(result));
            console.log('[Quiz] Result stored to localStorage:', result);
        }} catch (e) {{
            console.error('[Quiz] Error storing to localStorage:', e);
        }}

        // Store in window object (accessible from parent)
        window.quizResultData = JSON.stringify(result);
        console.log('[Quiz] Result stored in window.quizResultData');

        // Update the results display
        const resultsDiv = document.getElementById('streamlit-quiz-results');
        if (resultsDiv) {{
            resultsDiv.innerHTML = `
                <div style="padding: 20px; background: #e8f5e9; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #4caf50;">🎉 Quiz Completed!</h2>
                    <p style="font-size: 1.2rem;"><strong>Score: ${{score}}/${{total}} (${{percentage}}%)</strong></p>
                    <p>Time spent: ${{timeSpent}} seconds</p>
                    <p style="color: #666;">Click the button below to save your score!</p>
                </div>
            `;
        }}

        // Add a hidden div with the result as JSON (for st.js() to read)
        let hiddenDiv = document.getElementById('steam-quiz-hidden-result');
        if (!hiddenDiv) {{
            hiddenDiv = document.createElement('div');
            hiddenDiv.id = 'steam-quiz-hidden-result';
            hiddenDiv.style.display = 'none';
            document.body.appendChild(hiddenDiv);
        }}
        hiddenDiv.setAttribute('data-result', JSON.stringify(result));
        hiddenDiv.textContent = JSON.stringify(result);
        console.log('[Quiz] Result stored in hidden div #steam-quiz-hidden-result');

        console.log('[Quiz] Quiz completed:', {{ score, total, timeSpent }});
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

# Instructions and save button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.info("### After finishing the quiz:")
    st.markdown("1. ✅ Answer all questions")
    st.markdown("2. ✅ Click **Check Answers** in the quiz")
    st.markdown("3. ✅ Click the button below to save")

    if is_first_attempt:
        st.success("🎯 **First Attempt** - Your score will be recorded!")
    else:
        st.warning("📝 **Practice Mode** - This won't be recorded")

    if st.button("💾 Save My Quiz Result", type="primary", key="save_quiz_result"):
        # Use st.js() to directly read from the quiz iframe
        check_js = """(function() {
            console.log('[Save Button] Looking for quiz result...');

            // Find all iframes on the page
            const iframes = document.querySelectorAll('iframe');
            console.log('[Save Button] Found', iframes.length, 'iframes');

            // Try to find the quiz iframe and read its result
            for (let i = 0; i < iframes.length; i++) {
                try {
                    const iframe = iframes[i];
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

                    // Look for our hidden result div
                    const hiddenDiv = iframeDoc.getElementById('steam-quiz-hidden-result');
                    if (hiddenDiv) {
                        const resultStr = hiddenDiv.textContent || hiddenDiv.getAttribute('data-result');
                        if (resultStr) {
                            console.log('[Save Button] ✓ Found result in quiz iframe hidden div');
                            return JSON.parse(resultStr);
                        }
                    }

                    // Also check for window.quizResultData
                    const iframeWindow = iframe.contentWindow;
                    if (iframeWindow && iframeWindow.quizResultData) {
                        console.log('[Save Button] ✓ Found result in quiz iframe window.quizResultData');
                        return JSON.parse(iframeWindow.quizResultData);
                    }
                } catch (e) {
                    // Cross-origin restrictions, skip this iframe
                    console.log('[Save Button] Cannot access iframe', i, '-', e.message);
                }
            }

            // Fallback: check if result was stored in main window (via some other mechanism)
            if (window.steamQuizResult) {
                console.log('[Save Button] Found result in window.steamQuizResult');
                return window.steamQuizResult;
            }

            console.log('[Save Button] No quiz result found');
            return {error: 'No quiz result found. Please complete the quiz first and click Check Answers.'};
        })()"""

        # Try st.js() first (Streamlit 1.33+)
        try:
            result = st.js(check_js)

            if result:
                if isinstance(result, str):
                    data = json.loads(result)
                elif isinstance(result, dict):
                    data = result
                else:
                    data = None

                if data and data.get('error'):
                    st.warning(data['error'])
                    st.info("💡 Make sure you:")
                    st.info("1. ✅ Answered all questions")
                    st.info("2. ✅ Clicked 'Check Answers' in the quiz")
                    st.info("3. ✅ Waited for the score to appear")

                elif data and data.get('type') == 'quiz_completed' and is_first_attempt:
                    # Initialize quiz tracking in session state if not exists
                    if 'quiz_last_processed' not in st.session_state:
                        st.session_state.quiz_last_processed = {}

                    # Create unique attempt key to prevent duplicate processing
                    attempt_key = f"{quiz_id}_{data.get('timestamp', '')}"

                    if not st.session_state.quiz_last_processed.get(attempt_key):
                        # Record the quiz attempt
                        record_quiz_attempt(
                            st.session_state.user_id,
                            data['quizId'],
                            data['score'],
                            data['total'],
                            data.get('timeSpent', 0)
                        )

                        percentage = round(data['score'] / data['total'] * 100)

                        st.success(f"""
                            🎉 **First Attempt Saved!**
                            - Score: {data['score']}/{data['total']} ({percentage}%)
                            - Time: {data.get('timeSpent', 0)} seconds

                            Your result has been saved to the database!
                        """)
                        st.balloons()

                        # Mark as processed
                        st.session_state.quiz_last_processed[attempt_key] = True

                elif data and data.get('type') == 'quiz_completed' and not is_first_attempt:
                    st.info("📝 This was a practice attempt. Your score was not recorded (only first attempts count).")

        except AttributeError:
            # st.js() not available, show error message
            st.error("⚠️ Streamlit 1.33+ required for quiz saving. Please update Streamlit or contact your teacher.")
            st.info("For teachers: Run `pip install --upgrade streamlit` to enable quiz result saving.")

# Instructions
st.markdown("""
---
### Instructions
1. Answer all questions by selecting the best option
2. Click "Check Answers" when you're done
3. Click "💾 Save My Quiz Result" to save your score
4. Check "My Progress" to see your statistics
""")
