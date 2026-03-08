"""
Quiz Viewer Page
Displays the selected quiz and handles score submission.
"""

import streamlit as st
import os
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
# Current file is in streamlit_app/pages/, need to go up two levels to repo root
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
                    <p style="color: #666;">Your result has been saved!</p>
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
        }} catch (e) {{
            console.error('Error storing quiz result:', e);
        }}

        console.log('Quiz completed:', {{ score, total, timeSpent }});
    }};

    // Override checkAnswers function
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

# Insert the injected JS before closing body tag
if '</body>' in quiz_html:
    quiz_html = quiz_html.replace('</body>', injected_js + '</body>')
else:
    quiz_html = quiz_html.replace('</html>', injected_js + '</html>')

# Also append the original quiz JS
if quiz_js:
    quiz_html = quiz_html.replace('</body>', f'<script>{quiz_js}</script></body>')

# Display the quiz using st.html (Streamlit 1.31+)
try:
    st.html(quiz_html, height=800)
except Exception as e:
    # Fallback to components.v1.html for older Streamlit versions
    st.components.v1.html(quiz_html, height=800, scrolling=True)

# Poll for quiz completion - check localStorage periodically
# Use a button to manually trigger result check when quiz is done
st.markdown("---")

# Add a "Save My Result" button that students click after completing the quiz
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✅ I have finished the quiz - Save my result", type="primary", key="save_quiz_result"):
        # JavaScript to check localStorage and return the result
        check_js = f"""
        <script>
        (function() {{
            const resultStr = localStorage.getItem('steam_quiz_result');
            if (resultStr) {{
                try {{
                    const result = JSON.parse(resultStr);
                    const age = Date.now() - (result.timestamp || 0);

                    // Only process if result is for this quiz and less than 5 minutes old
                    if (result.quizId === '{quiz_id}' && age < 300000) {{
                        // Return the result via Streamlit component API
                        if (typeof Streamlit !== 'undefined' && Streamlit.setComponentValue) {{
                            Streamlit.setComponentValue(result);
                            localStorage.removeItem('steam_quiz_result');
                        }}
                    }}
                }} catch (e) {{
                    console.error('Error:', e);
                }}
            }} else {{
                if (typeof Streamlit !== 'undefined' && Streamlit.setComponentValue) {{
                    Streamlit.setComponentValue({{error: 'No quiz result found. Please complete the quiz first.'}});
                }}
            }}
        }})();
        </script>
        """

        result_component = st.components.v1.html(check_js, height=0)

        # Process the result
        if result_component:
            if isinstance(result_component, dict) and result_component.get('error'):
                st.warning(result_component['error'])
            elif isinstance(result_component, dict) and result_component.get('type') == 'quiz_completed':
                data = result_component

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
                        🎉 **Quiz Completed!**
                        - Score: {data['score']}/{data['total']} ({percentage}%)
                        - Time: {data.get('timeSpent', 0)} seconds

                        Your result has been saved!
                    """)
                    st.balloons()

                    # Mark as processed
                    st.session_state.quiz_last_processed[attempt_key] = True

                    # Rerun to show success message
                    st.rerun()

# Instructions
st.markdown("""
### Instructions
1. Answer all questions by selecting the best option
2. Click "Check Answers" when you're done
3. Click the "Save My Result" button below to save your score
4. You can retake the quiz to improve your score!
""")
