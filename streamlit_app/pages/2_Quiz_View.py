"""
Quiz Viewer Page
Displays the selected quiz in an iframe and handles score submission.
"""

import streamlit as st
import os
import time
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
# Determine the base directory - works both locally and on Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate to parent directory (streamlit_app) then to quizzes
base_dir = os.path.dirname(current_dir)
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

# Create a modified version of the quiz HTML with score reporting
# Read the original HTML
with open(quiz_path, 'r', encoding='utf-8') as f:
    quiz_html = f.read()

# Inject score reporting script
score_script = f"""
<script>
// Override the showResults function to report score to Streamlit
const originalShowResults = window.showResults;
const originalCheckAnswers = window.checkAnswers;

// Store quiz info
window.quizId = "{quiz_id}";
window.userId = {st.session_state.user_id};
window.startTime = Date.now();

// Intercept checkAnswers to track completion
if (typeof window.checkAnswers === 'function') {{
    const originalCheckAnswers = window.checkAnswers;
    window.checkAnswers = function() {{
        const result = originalCheckAnswers.apply(this, arguments);
        // Wait a bit for results to be calculated
        setTimeout(() => {{
            sendScoreToStreamlit();
        }}, 500);
        return result;
    }};
}}

function sendScoreToStreamlit() {{
    // Try to find the score
    let score = 0;
    let total = {quiz['questions']};

    // Try to get score from various possible locations
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

    // Send to parent
    const timeSpent = Math.round((Date.now() - window.startTime) / 1000);
    window.parent.postMessage({{
        type: 'quiz_completed',
        quizId: "{quiz_id}",
        userId: {st.session_state.user_id},
        score: score,
        total: total,
        timeSpent: timeSpent
    }}, '*');

    console.log('Score sent:', {{ score, total, timeSpent }});
}}

// Also try to intercept the results display
const observer = new MutationObserver((mutations) => {{
    mutations.forEach((mutation) => {{
        if (mutation.addedNodes.length) {{
            mutation.addedNodes.forEach((node) => {{
                if (node.id === 'results' || node.classList?.contains('results')) {{
                    setTimeout(sendScoreToStreamlit, 100);
                }}
            }});
        }}
    }});
}});

observer.observe(document.body, {{ childList: true, subtree: true }});
</script>
"""

# Insert the script before closing body tag
if '</body>' in quiz_html:
    quiz_html = quiz_html.replace('</body>', score_script + '</body>')
else:
    quiz_html += score_script

# Display the quiz in a container that can receive postMessages
st.markdown("""
<style>
    .quiz-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        overflow: hidden;
        background: white;
    }
    .quiz-frame {
        width: 100%;
        min-height: 700px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Create a temporary file with the modified HTML
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
    tmp.write(quiz_html)
    tmp_path = tmp.name

# Display instructions
st.info("""
    👆 **Complete the quiz above!** Your score will be automatically saved when you click "Check Answers".
    You can take the quiz multiple times - your best score will be recorded.
""")

# Inject JavaScript to receive postMessages from iframe
st.markdown(f"""
<script>
// Listen for messages from the quiz iframe
window.addEventListener('message', function(event) {{
    if (event.data.type === 'quiz_completed') {{
        // Store in session state
        const payload = {{
            quiz_id: event.data.quizId,
            user_id: event.data.userId,
            score: event.data.score,
            total: event.data.total,
            time_spent: event.data.timeSpent
        }};

        // Send to Streamlit via hidden input
        const input = document.getElementById('quiz-completed-data');
        if (input) {{
            input.value = JSON.stringify(payload);
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}
}});
</script>
<input type="hidden" id="quiz-completed-data" value="">
""", unsafe_allow_html=True)

# Display the quiz
st.components.v1.iframe(
    src=f"file://{tmp_path}",
    height=700,
    scrolling=True
)

# Hidden input to receive data from JavaScript
quiz_result = st.text_input("", key="quiz_completed_data", label_visibility="collapsed")

# Process the result when received
if quiz_result:
    try:
        import json
        data = json.loads(quiz_result)
        record_quiz_attempt(
            data['user_id'],
            data['quiz_id'],
            data['score'],
            data['total'],
            data.get('time_spent', 0)
        )
        st.success(f"""
            🎉 **Quiz completed!**
            - Score: {data['score']}/{data['total']} ({round(data['score']/data['total']*100)}%)
            - Time: {data.get('time_spent', 0)} seconds

            Your result has been saved!
        """)
        st.balloons()
    except Exception as e:
        st.error(f"Error saving quiz result: {e}")

# Cleanup temp file
try:
    os.unlink(tmp_path)
except:
    pass
