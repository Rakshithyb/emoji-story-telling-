import streamlit as st
import os
import random
from dotenv import load_dotenv
import streamlit.components.v1 as components

load_dotenv()

# Must be the first streamlit command
st.set_page_config(page_title="Emoji-Only Story Challenge", page_icon="🎭", layout="centered")

from agent.graph import graph

def set_custom_css():
    st.markdown("""
        <style>
        html {
            scroll-behavior: smooth;
        }
        .stApp {
            background: linear-gradient(135deg, #1e1e2f, #2b2d42);
            color: white;
        }
        h1, h2, h3 {
            color: white !important;
            font-family: 'Inter', sans-serif;
            text-align: center;
        }
        /* ===== Base Button Style ===== */
        div.stButton > button,
        div.stForm button {
            background: linear-gradient(135deg, #6C63FF, #8B7BFF) !important;
            color: white !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 18px rgba(108, 99, 255, 0.5) !important;
            width: 100% !important;
        }

        /* ===== Hover ===== */
        div.stButton > button:hover,
        div.stForm button:hover {
            transform: translateY(-3px) !important;
            filter: brightness(1.1) !important;
        }

        /* ===== Click ===== */
        div.stButton > button:active,
        div.stForm button:active {
            transform: translateY(0px) !important;
            filter: brightness(0.9) !important;
        }

        /* ===== Disabled ===== */
        div.stButton > button:disabled,
        div.stForm button:disabled {
            background: #555 !important;
            color: #ddd !important;
            box-shadow: none !important;
        }

        /* ===== Accent Button Mapping ===== */
        button[kind="secondary"] {
            background: linear-gradient(135deg, #FF6584, #FF8FA3) !important;
            box-shadow: 0 6px 18px rgba(255, 101, 132, 0.5) !important;
        }
        /* ===== Text Input Container ===== */
        div[data-testid="stTextInput"] input {
            background-color: #1E1E2F !important;
            color: #FFFFFF !important;
            border: 2px solid #6C63FF !important;
            border-radius: 14px !important;
            padding: 14px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
        }

        /* ===== Placeholder Text ===== */
        div[data-testid="stTextInput"] input::placeholder {
            color: #B8B8D1 !important;
            opacity: 1 !important;
        }

        /* ===== Focus Effect ===== */
        div[data-testid="stTextInput"] input:focus {
            border: 2px solid #FF6584 !important;
            box-shadow: 0 0 12px rgba(255, 101, 132, 0.6) !important;
            outline: none !important;
        }

        /* ===== Remove Default Grey Shadow ===== */
        div[data-testid="stTextInput"] {
            background: transparent !important;
        }

        /* ===== Helper Text Style ===== */
        div[data-testid="stTextInput"] small {
            color: #A0A0C0 !important;
            font-size: 12px !important;
        }
        
        /* Card Style Container */
        .card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .fade-in {
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Emoji Display Improvement */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        .emoji-display {
            font-size: 60px;
            text-align: center;
            padding: 20px;
            background-color: rgba(255,255,255,0.05);
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(108,99,255,0.5);
            animation: float 3s ease-in-out infinite;
            margin-bottom: 20px;
        }
        
        .score-badge {
            text-align: center;
            color: #FF6584;
            font-family: 'Inter', sans-serif;
            font-weight: bold;
        }

        /* ===== Sidebar Background ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e1e2f, #2b2d42) !important;
            color: white !important;
        }

        /* Sidebar text */
        section[data-testid="stSidebar"] * {
            color: #EAEAF0 !important;
        }

        /* Sidebar headers */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFB86C !important;
        }

        /* Remove light grey default block background */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Optional subtle divider */
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

if not os.environ.get("GROQ_API_KEY"):
    st.error("🚨 Please set `GROQ_API_KEY` in your `.env` file or environment variables to begin.")
    st.stop()

set_custom_css()

st.markdown("<div class='fade-in card'>", unsafe_allow_html=True)
st.markdown("<h1>🎭 Emoji Story Challenge</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a19cc5; font-size: 18px;'>Can you decipher the story from just emojis?</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Thread management for memory
if "thread_id" not in st.session_state:
    import uuid
    st.session_state.thread_id = str(uuid.uuid4())

# Session state to track if gameplay started
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}

def get_current_state():
    state = graph.get_state(thread_config)
    if state and hasattr(state, 'values') and state.values:
        return state.values
    return {}

# ------------------------------------------------------------------
# SECTION 1: DIFFICULTY SELECTION / START VIEW
# ------------------------------------------------------------------
if not st.session_state.game_started:
    st.markdown("<div class='fade-in card'>", unsafe_allow_html=True)
    st.markdown("### First, pick your challenge level!")
    
    difficulty = st.selectbox(
        "Choose Difficulty",
        ["Easy", "Medium", "Hard"]
    )
    
    if st.button("🚀 Start Game"):
        st.session_state.game_started = True
        st.session_state.refresh_counter = 0
        gen_id = f"{difficulty}_{st.session_state.refresh_counter}_{random.randint(1000, 9999)}"
        st.session_state.generation_id = gen_id
        
        with st.spinner(f"🤖 Conjuring a visually stunning {difficulty} emoji story..."):
            graph.invoke({
                "difficulty": difficulty,
                "selected_story": "",
                "emoji_story": "", 
                "score": 0, 
                "history": [],
                "hints_revealed": 0,
                "story_metadata": {},
                "refresh_counter": st.session_state.refresh_counter,
                "generation_id": gen_id
            }, thread_config)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_state = get_current_state()

# Provide DEBUG info cleanly
st.markdown(f"<p style='text-align:center; color: #a19cc5; font-size:12px;'>DEBUG Generation ID: {current_state.get('generation_id', 'Unknown')}</p>", unsafe_allow_html=True)

# Layout Headers
score = current_state.get("score", 0)
history = current_state.get("history", [])
round_num = len(history) + 1
current_difficulty = current_state.get("difficulty", "Medium")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='card score-badge'>🔄 Round: {round_num}<br><span style='font-size:12px; color:#a19cc5;'>Difficulty: {current_difficulty}</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='card score-badge'><h3>🏆 Score: {score}</h3></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SECTION 2: EMOJI STORY
# ------------------------------------------------------------------
emoji_story = current_state.get("emoji_story", "🤔")

st.markdown("<a id='story'></a>", unsafe_allow_html=True)
st.markdown(f"<div class='fade-in'>", unsafe_allow_html=True)
st.markdown(f"<div class='emoji-display'>{emoji_story}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SECTION 3 + 4: GUESS INPUT & HINTS
# ------------------------------------------------------------------
if not current_state.get("evaluation_result"):
    
    col_ref1, col_ref2, col_ref3 = st.columns([1, 2, 1])
    with col_ref2:
        if st.button("🔄 Refresh Story", use_container_width=True):
            st.session_state.refresh_counter += 1
            gen_id = f"{current_difficulty}_{st.session_state.refresh_counter}_{random.randint(1000, 9999)}"
            st.session_state.generation_id = gen_id
            
            with st.spinner("Generating a completely new story..."):
                graph.invoke({
                    "selected_story": "",
                    "emoji_story": "", 
                    "user_guess": "", 
                    "evaluation_result": "", 
                    "explanation": "", 
                    "feedback": "",
                    "hints_revealed": 0,
                    "story_metadata": {},
                    "refresh_counter": st.session_state.refresh_counter,
                    "generation_id": gen_id
                }, thread_config)
            st.rerun()

    meta = current_state.get("story_metadata", {})
    hints_revealed = current_state.get("hints_revealed", 0)

    # HINT SECTION
    if meta:
        st.markdown("<div class='fade-in card'>", unsafe_allow_html=True)
        allowed_hints = [
            ("Story Type", meta.get("story_type")),
            ("Setting", meta.get("setting_hint")),
            ("Main Character", meta.get("main_character_hint")),
            ("Central Conflict", meta.get("central_conflict")),
            ("Theme", meta.get("theme"))
        ]
        
        if hints_revealed > 0:
            st.markdown("### 💡 Hints")
            for i in range(min(hints_revealed, len(allowed_hints))):
                key, val = allowed_hints[i]
                st.info(f"**{key}:** {val}")
        
        # Deduct score if hints triggered
        if hints_revealed < len(allowed_hints):
            if st.button("💡 Reveal Hint (-1 point)"):
                new_revealed = hints_revealed + 1
                new_score = current_state.get("score", 0) - 1
                graph.update_state(thread_config, {"hints_revealed": new_revealed, "score": new_score})
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # INPUT SECTION
    st.markdown("<div class='fade-in card'>", unsafe_allow_html=True)
    with st.form("guess_form"):
        user_guess = st.text_input("💡 Your Guess (Movie, Event, Concept):", placeholder="e.g. Star Wars, The French Revolution...")
        submitted = st.form_submit_button("Submit Guess ✨")
        
        if submitted:
            if user_guess.strip():
                with st.spinner("🧠 Analyzing your guess..."):
                    graph.invoke({"user_guess": user_guess.strip()}, thread_config)
                st.rerun()
            else:
                st.warning("Please enter a guess before submitting.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_x1, col_x2, col_x3 = st.columns([1, 2, 1])
    with col_x2:
        if st.button("⏪ Change Difficulty / Restart"):
            st.session_state.game_started = False
            st.rerun()

# ------------------------------------------------------------------
# SECTION 5: REVEAL + EXPLANATION
# ------------------------------------------------------------------
else:
    result = current_state.get("evaluation_result", "")
    feedback = current_state.get("feedback", "")
    explanation = current_state.get("explanation", "")
    user_guess = current_state.get("user_guess", "")
    selected_story = current_state.get("selected_story", "Unknown")
    
    st.markdown("<div class='fade-in card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Evaluation")
    st.markdown(f"**Your Guess:** `{user_guess}`")
    
    if result == "Correct":
        st.success(f"🎉 **{result}!** {feedback}")
        st.balloons()
    elif result == "Partially Correct":
        st.warning(f"🤔 **{result}!** {feedback}")
    else:
        st.error(f"❌ **{result}!** {feedback}")
    st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div class='fade-in card' style='background:rgba(108,99,255,0.1); border:1px solid #6C63FF;'>", unsafe_allow_html=True)
    st.markdown("### 📖 The Real Story")
    st.markdown(f"<h3 style='color:#FF6584 !important;'>{selected_story}</h3>", unsafe_allow_html=True)
    st.info(explanation)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Next Round", use_container_width=True):
            st.session_state.refresh_counter += 1
            gen_id = f"{current_difficulty}_{st.session_state.refresh_counter}_{random.randint(1000, 9999)}"
            st.session_state.generation_id = gen_id
            
            with st.spinner("Preparing the next challenge..."):
                graph.invoke({
                    "selected_story": "",
                    "emoji_story": "", 
                    "user_guess": "", 
                    "evaluation_result": "", 
                    "explanation": "", 
                    "feedback": "",
                    "hints_revealed": 0,
                    "story_metadata": {},
                    "refresh_counter": st.session_state.refresh_counter,
                    "generation_id": gen_id
                }, thread_config)
            st.rerun()
    with col2:
        if st.button("⏪ Change Difficulty", use_container_width=True):
            st.session_state.game_started = False
            st.rerun()

# ------------------------------------------------------------------
# COMPONENT SCRIPT INJECTION: AUTO SCROLL
# ------------------------------------------------------------------
if st.session_state.game_started:
    components.html(
        """
        <script>
        const el = window.parent.document.getElementById("story");
        if (el) { el.scrollIntoView({behavior: "smooth"}); }
        </script>
        """,
        height=0
    )


# Leaderboard / Side bar logic
with st.sidebar:
    st.markdown("## 📜 Game History")
    if not history:
        st.write("No history... yet!")
    else:
        for idx, rnd in enumerate(history):
            with st.expander(f"Round {idx+1} ({rnd.get('result')})"):
                st.write(f"**Emojis:** {rnd.get('emoji_story')}")
                st.write(f"**Story:** {rnd.get('selected_story')}")
                st.write(f"**Your Guess:** {rnd.get('user_guess')}")
                st.write(f"**Points Earned:** +{rnd.get('points_earned')}")
