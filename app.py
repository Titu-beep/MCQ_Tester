import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# -- Page Config --
st.set_page_config(
    page_title="Premium MCQ Tester",
    page_icon="🎯",
    layout="centered",
)

# -- Custom CSS for Premium Look --
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Header Banner */
    .banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
    }
    .banner h1 { margin: 0; font-size: 2.5rem; font-weight: 800; color: white; }
    .banner p { margin-top: 0.5rem; opacity: 0.9; font-size: 1.1rem; color: white; }

    /* Quiz Card */
    .q-card {
        background: #1e293b;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .q-text { font-size: 1.25rem; font-weight: 600; line-height: 1.6; color: #f1f5f9; }
    
    /* Result Card */
    .result-card {
        background: #1e293b;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        border: 1px solid #6366f1;
    }
    
    /* Sidebar Navigation */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    .nav-btn {
        width: 100%;
        margin-bottom: 0.5rem;
        text-align: left;
    }
    
    /* Result Table */
    .result-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: #1e293b;
        border-radius: 12px;
        overflow: hidden;
    }
    .result-table th, .result-table td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid #334155;
    }
    .result-table th { background: #334155; color: #94a3b8; font-weight: 600; }
    .correct { color: #22c55e; }
    .wrong { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# -- Helpers --
OPTION_COLS_POSSIBLE = [
    ["Option A", "Option B", "Option C", "Option D"],
    ["option a", "option b", "option c", "option d"],
    ["A", "B", "C", "D"],
    ["a", "b", "c", "d"],
    ["Option1", "Option2", "Option3", "Option4"],
    ["Choice1", "Choice2", "Choice3", "Choice4"],
]

def find_col(df_cols, candidates):
    lower = {c.lower().strip(): c for c in df_cols}
    for cand in candidates:
        if cand.lower().strip() in lower:
            return lower[cand.lower().strip()]
    return None

def load_data(file, save=True):
    try:
        # If it's a string path (from past sets)
        if isinstance(file, str):
            if file.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        else:
            # It's an uploaded file object
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            if save:
                save_path = os.path.join("sets", file.name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
        
        df.columns = df.columns.astype(str).str.strip()
        
        # Detect Question Column
        q_col = find_col(df.columns, ["Question", "question", "Q", "q", "Ques"])
        # Detect Answer Column
        a_col = find_col(df.columns, ["Answer", "answer", "Ans", "ans", "Correct Answer"])
        
        # Detect Option Columns
        opt_cols = []
        for group in OPTION_COLS_POSSIBLE:
            found = [find_col(df.columns, [g]) for g in group]
            if all(found):
                opt_cols = found
                break
        
        if not q_col or not a_col or not opt_cols:
            missing = []
            if not q_col: missing.append("Question")
            if not a_col: missing.append("Answer")
            if not opt_cols: missing.append("Options (A, B, C, D)")
            st.error(f"⚠️ Missing columns: {', '.join(missing)}")
            return None

        # Standardize
        df_clean = pd.DataFrame()
        df_clean['Question'] = df[q_col]
        df_clean['Option A'] = df[opt_cols[0]]
        df_clean['Option B'] = df[opt_cols[1]]
        df_clean['Option C'] = df[opt_cols[2]]
        df_clean['Option D'] = df[opt_cols[3]]
        df_clean['Answer'] = df[a_col]
        
        return df_clean.dropna(subset=['Question'])
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# -- Session State --
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'test_date' not in st.session_state:
    st.session_state.test_date = None

# -- App Logic --
st.markdown('<div class="banner"><h1>🎯 MCQ Master</h1><p>Test your knowledge with ease</p></div>', unsafe_allow_html=True)

if not st.session_state.quiz_started:
    st.subheader("📤 New Test")
    uploaded_file = st.file_uploader("Choose an Excel/CSV file", type=['xlsx', 'csv'])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success(f"Loaded {len(df)} questions!")
            if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
                st.session_state.questions = df.to_dict('records')
                st.session_state.quiz_started = True
                st.session_state.current_q = 0
                st.session_state.user_answers = {}
                st.session_state.start_time = time.time()
                st.session_state.test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.end_time = None
                st.rerun()

    st.divider()
    st.subheader("🕒 Past MCQ Sets")
    if not os.path.exists("sets"):
        os.makedirs("sets")
    
    past_files = [f for f in os.listdir("sets") if f.endswith(('.xlsx', '.csv'))]
    if past_files:
        selected_past = st.selectbox("Select a previous set:", past_files, index=None)
        if selected_past:
            if st.button(f"🚀 Load {selected_past}", use_container_width=True):
                df = load_data(os.path.join("sets", selected_past), save=False)
                if df is not None:
                    st.session_state.questions = df.to_dict('records')
                    st.session_state.quiz_started = True
                    st.session_state.current_q = 0
                    st.session_state.user_answers = {}
                    st.session_state.start_time = time.time()
                    st.session_state.test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.end_time = None
                    st.rerun()
    else:
        st.info("No past sets found. Upload a file to see it here later!")

elif st.session_state.quiz_started and st.session_state.current_q < len(st.session_state.questions):
    questions = st.session_state.questions
    idx = st.session_state.current_q
    q_data = questions[idx]
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🧩 Navigation")
        for i in range(len(questions)):
            status = "⚪"
            if i in st.session_state.user_answers:
                status = "✅" 
            if i == idx:
                status = "🎯"
            
            if st.button(f"{status} Question {i+1}", key=f"nav_{i}", use_container_width=True):
                st.session_state.current_q = i
                st.rerun()
        
        st.divider()
        if st.button("🏁 Finish Quiz", type="secondary", use_container_width=True):
            st.session_state.current_q = len(questions)
            st.session_state.end_time = time.time()
            st.rerun()

    # Progress
    progress = (idx + 1) / len(questions)
    st.progress(progress, text=f"Question {idx + 1} of {len(questions)}")
    
    st.markdown(f'<div class="q-card"><div class="q-text">{q_data["Question"]}</div></div>', unsafe_allow_html=True)
    
    options = [q_data['Option A'], q_data['Option B'], q_data['Option C'], q_data['Option D']]
    
    # Pre-select if already answered
    saved_answer = st.session_state.user_answers.get(idx)
    choice_idx = None
    if saved_answer in options:
        choice_idx = options.index(saved_answer)

    choice = st.radio("Select an answer:", options, index=choice_idx, key=f"q_{idx}")
    
    if choice:
        st.session_state.user_answers[idx] = choice

    col_back, col_next = st.columns(2)
    
    with col_back:
        if st.button("⬅️ Previous", use_container_width=True, disabled=idx == 0):
            st.session_state.current_q -= 1
            st.rerun()
            
    with col_next:
        btn_label = "Next ➡️" if idx < len(questions) - 1 else "See Results 🏁"
        if st.button(btn_label, type="primary", use_container_width=True):
            if idx < len(questions) - 1:
                st.session_state.current_q += 1
            else:
                st.session_state.current_q = len(questions)
                st.session_state.end_time = time.time()
            st.rerun()

else:
    # Final Results
    duration = 0
    if st.session_state.end_time and st.session_state.start_time:
        duration = round(st.session_state.end_time - st.session_state.start_time, 2)
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.balloons()
    st.header("Quiz Complete! 🏁")
    
    total = len(st.session_state.questions)
    # Calculate score
    score = 0
    results_data = []
    for i, q in enumerate(st.session_state.questions):
        user_ans = st.session_state.user_answers.get(i, "Not Answered")
        is_correct = str(user_ans).strip() == str(q['Answer']).strip()
        if is_correct:
            score += 1
        
        results_data.append({
            "Question": q['Question'],
            "Your Answer": user_ans,
            "Correct Answer": q['Answer'],
            "Result": "Correct" if is_correct else "Wrong"
        })

    percentage = (score / total) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score} / {total}")
    col2.metric("Percentage", f"{percentage:.1f}%")
    col3.metric("Time Taken", f"{duration}s")
    
    st.markdown(f"**Date:** {st.session_state.test_date}")
    
    if percentage >= 80:
        st.success("Excellent! You're a master! 🌟")
    elif percentage >= 50:
        st.info("Good job! Keep practicing! 💪")
    else:
        st.warning("Keep learning, you'll get there! 📚")

    # Download Results
    df_results = pd.DataFrame(results_data)
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_results.to_excel(writer, index=False, sheet_name='Results')
    processed_data = output.getvalue()
    
    st.download_button(
        label="📥 Download Results (Excel)",
        data=processed_data,
        file_name=f"quiz_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    if st.button("🔄 Try Again"):
        st.session_state.quiz_started = False
        st.session_state.user_answers = {}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Review Table
    st.subheader("🔍 Review Answers")
    for item in results_data:
        color = "correct" if item['Result'] == "Correct" else "wrong"
        with st.expander(f"{'✅' if item['Result'] == 'Correct' else '❌'} {item['Question']}"):
            st.markdown(f"**Your Answer:** <span class='{color}'>{item['Your Answer']}</span>", unsafe_allow_html=True)
            if item['Result'] == "Wrong":
                st.markdown(f"**Correct Answer:** <span class='correct'>{item['Correct Answer']}</span>", unsafe_allow_html=True)
