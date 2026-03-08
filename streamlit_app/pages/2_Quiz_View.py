"""
Quiz Viewer Page
Displays the selected quiz and handles score submission.
"""

import streamlit as st
import os
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
if os_path.exists(js_path):
    with open(js_path, 'r', encoding='utf-8') as f:
        quiz_js = f.read()

# Insert JavaScript to show score when quiz completes
# This will store result in window.steamQuizResult for st.javascript() to read
injected_js = f"""
<script>
// Streamlit Quiz Integration
(function() {{
    window.quizId = "{quiz_id}";
    window.userId = {st.session_state.user_id};
    window.startTime = Date.now();
    window.quizCompleted = false;
    window.steamQuizResult = null;  // Global variable for st.javascript() to read

    // Function to show score when quiz completes
    window.reportScore = function(score, total) {{
        if (window.quizCompleted) return;
        window.quizCompleted = true;

        const timeSpent = Math.round((Date.now() - window.startTime) / 1000);
        const percentage = Math.round((score / total) * 100);

        // STORE RESULT FOR PYTHON TO READ
        window.steamQuizResult = {{
            quizId: "{quiz_id}",
            userId: {st.session_state.user_id},
            score: score,
            total: total,
            timeSpent: timeSpent,
            timestamp: Date.now()
        }};
        console.log('[Quiz] Result stored in window.steamQuizResult:', window.steamQuizResult);

        // Update the results display
        const resultsDiv = document.getElementById('streamlit-quiz-results');
        if (resultsDiv) {{
            resultsDiv.innerHTML = `
                <div style="padding: 20px; background: #e8f5e9; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #4caf50;">🎉 Quiz Completed!</h2>
                    <p style="font-size: 1.2rem;"><strong>Score: ${{score}}/${{total}} (${{percentage}}%)</strong></p>
                    <p>Time spent: ${{timeSpent}} seconds</p>
                    <p style="color: #666;">✅ Saving your score...</p>
                </div>
            `;
        }}

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

# ============================================================================
# AUTO-SCORE DETECTION WITH st.javascript()
# ============================================================================

st.markdown("---")

# Status display area
status_placeholder = st.empty()

# Check for quiz result using st.javascript()
# This runs in the MAIN page context and can access the quiz iframe
quiz_saved = False
if hasattr(st, 'javascript'):
    check_js = f"""
    (function() {{
        // Find all iframes that might contain the quiz
        const iframes = document.querySelectorAll('iframe');

        for (let iframe of iframes) {{
            try {{
                const iframeWindow = iframe.contentWindow;
                if (iframeWindow && iframeWindow.steamQuizResult) {{
                    const result = iframeWindow.steamQuizResult;
                    console.log('[st.js] Found quiz result:', result);

                    // Clear the result to prevent duplicate saves
                    iframeWindow.steamQuizResult = null;

                    // Return the result as a JSON string
                    return JSON.stringify(result);
                }}
            }} catch (e) {{
                // Cross-origin or other access issues - try next iframe
                continue;
            }}
        }}

        // No result found yet
        console.log('[st.js] No quiz result found yet');
        return null;
    }})();
    """

    quiz_result_json = st.javascript(check_js)

    if quiz_result_json:
        import json
        try:
            quiz_result = json.loads(quiz_result_json)

            # Verify this result is for the current quiz
            if quiz_result.get('quizId') == quiz_id:
                score = quiz_result.get('score', 0)
                total = quiz_result.get('total', int(quiz['questions']))
                time_spent = quiz_result.get('timeSpent', 0)

                if is_first_attempt:
                    # Record the quiz attempt automatically
                    record_quiz_attempt(
                        st.session_state.user_id,
                        quiz_id,
                        int(score),
                        int(total),
                        int(time_spent)
                    )

                    percentage = round((int(score) / int(total)) * 100)

                    status_placeholder.success(f"""
                        🎉 **Quiz Auto-Saved!**
                        - Score: {score}/{total} ({percentage}%)
                        - Time: {time_spent} seconds

                        Your result has been saved to the database!
                    """)
                    st.balloons()
                    quiz_saved = True
                else:
                    status_placeholder.info(f"📝 Practice: {score}/{total} (not recorded - only first attempts count)")

                # Rerun to update the UI and prevent duplicate saves
                st.rerun()
        except json.JSONDecodeError as e:
            status_placeholder.warning(f"⚠️ Error reading quiz result. Please try manual entry.")
            print(f"[DEBUG] JSON decode error: {e}, got: {quiz_result_json}")

# Show status message
if not quiz_saved:
    if is_first_attempt:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔄 Check for Quiz Result", use_container_width=True, type="primary"):
                st.rerun()

        status_placeholder.info("⏳ Complete the quiz above, then click **Check for Quiz Result** to auto-save!")
    else:
        status_placeholder.info("📝 Practice Mode - Complete the quiz above for practice")

# Manual fallback (always available)
with st.expander("📝 Manual Score Entry"):
    st.markdown("If auto-save doesn't work, enter your score manually:")

    col_a, col_b = st.columns(2)
    with col_a:
        score_input = st.number_input(
            "Your Score",
            min_value=0,
            max_value=int(quiz['questions']),
            value=0,
            step=1,
            key=f"manual_score_{quiz_id}"
        )

    with col_b:
        if st.button("💾 Save Manual Result", type="secondary", key=f"manual_save_{quiz_id}"):
            if score_input > 0:
                if is_first_attempt:
                    record_quiz_attempt(
                        st.session_state.user_id,
                        quiz_id,
                        int(score_input),
                        int(quiz['questions']),
                        0
                    )
                    st.success(f"🎉 Manual save successful: {score_input}/{quiz['questions']}")
                    st.balloons()
                    st.rerun()
                else:
                    st.info(f"📝 Practice: {score_input}/{quiz['questions']} (not recorded)")

# Instructions
st.markdown("""
---
### Instructions
1. Answer all questions by selecting the best option
2. Click "Check Answers" when you're done
3. Click **"Check for Quiz Result"** button below to auto-save ✨
4. Or use Manual Score Entry if needed
5. Check "My Progress" to see your statistics
""")
