import streamlit as st
import pandas as pd
from groq import Groq

# ----------------------------------------------------
# 1) Hide GitHub link and Streamlit action button
# ----------------------------------------------------
HIDE_GITHUB_STYLE = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(HIDE_GITHUB_STYLE, unsafe_allow_html=True)

# ----------------------------------------------------
# 2) API Key Setup
# ----------------------------------------------------
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# ----------------------------------------------------
# 3) Prompt Functions: No Spinners, No Streaming
# ----------------------------------------------------
def prompt(text, prompt_type, base=''):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt_type["system_message"]},
            {"role": "user", "content": base + text}
        ],
        temperature=prompt_type["temperature"],
        max_tokens=1024,
        top_p=1,
        stream=False,  # no streaming
        stop=None,
    )
    # Directly read the response
    return completion.choices[0].message.content

prompt_creative = {
    "system_message": "You are a teacher. You should create content or questions based on the topic.",
    "temperature": 0.8,
}
prompt_strict = {
    "system_message": "You are a teacher. You should evaluate the answer based on the question.",
    "temperature": 0.2,
}

def generate_question(main_topic, subtopic, level):
    text = f"Generate a {level} level question in {main_topic}, focusing on {subtopic}."
    return prompt(text, prompt_creative, base="Make it unique: ")

def evaluate_answer(question, answer):
    text = f"Strictly evaluate: {answer} for Q: {question}."
    return prompt(text, prompt_strict)

def generate_explanation(question, answer):
    text = f"Give a thorough explanation for the correct answer to: {question}, user answer: {answer}"
    return prompt(text, prompt_creative, base="Detailed explanation: ")

def generate_personalized_tip(question, level):
    text = f"Provide tips for a {level} learner about question: {question}"
    return prompt(text, prompt_creative, base="Personalized tips: ")

def generate_personalized_learning_track(main_topic, level):
    text = f"Create a personalized {level} learning track for: {main_topic}"
    return prompt(text, prompt_creative, base="Dynamic track: ")

def get_next_level(current_level):
    levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
    if current_level in levels:
        idx = levels.index(current_level)
        if idx < len(levels) - 1:
            return levels[idx + 1]
    return current_level

def generate_level_based_questions(main_topic, subtopics, current_level, mix_next_level=False):
    questions = []
    next_level = get_next_level(current_level)
    for sub in subtopics:
        questions.append( (current_level, sub, generate_question(main_topic, sub, current_level)) )
        if mix_next_level and current_level != next_level:
            questions.append( (next_level, sub, generate_question(main_topic, sub, next_level)) )
    return questions

# ----------------------------------------------------
# 4) Session State Initialization
# ----------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "main_topic" not in st.session_state:
    st.session_state.main_topic = ""
if "subtopics" not in st.session_state:
    st.session_state.subtopics = []
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []

if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "final_questions" not in st.session_state:
    st.session_state.final_questions = []
if "final_answers" not in st.session_state:
    st.session_state.final_answers = []

# ----------------------------------------------------
# 5) Page Title
# ----------------------------------------------------
st.title("Minimal Multi-Step App (No Spinners, Single Click)")

# ----------------------------------------------------
# STEP 1: Enter Topic & Subtopics
# ----------------------------------------------------
if st.session_state.step == 1:
    st.header("Step 1: Topic & Subtopics")
    with st.form(key="form_step1"):
        topic_input = st.text_input("Main Topic:", value=st.session_state.main_topic)
        subs_input = st.text_input("Subtopics (comma separated):", value=", ".join(st.session_state.subtopics))
        submit1 = st.form_submit_button("Generate Questions")
    if submit1:
        if topic_input and subs_input:
            st.session_state.main_topic = topic_input
            st.session_state.subtopics = [s.strip() for s in subs_input.split(",") if s.strip()]
            # Generate questions for all levels
            combined = []
            for lvl in ["Beginner","Elementary","Intermediate","Upper Intermediate","Advanced"]:
                combined.extend(generate_level_based_questions(st.session_state.main_topic, st.session_state.subtopics, lvl))
            st.session_state.questions = combined
            st.session_state.answers = [""] * len(combined)
            st.session_state.step = 2
            st.experimental_rerun()
        else:
            st.warning("Please fill both fields.")

# ----------------------------------------------------
# STEP 2: Show Questions, Collect Answers
# ----------------------------------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Answer the Questions")
    for i, (lvl, sub, q) in enumerate(st.session_state.questions):
        st.write(f"**({lvl})** {sub} => {q}")
        st.session_state.answers[i] = st.text_area(f"Answer {i+1}", value=st.session_state.answers[i], key=f"a_{i}")
    if st.button("Submit Answers"):
        # Simple scoring: non-empty answers
        total = len(st.session_state.answers)
        correct = sum(1 for a in st.session_state.answers if a.strip())
        ratio = correct / total if total else 0
        if ratio >= 0.8:
            st.session_state.user_level = "Advanced"
        elif ratio >= 0.6:
            st.session_state.user_level = "Upper Intermediate"
        elif ratio >= 0.4:
            st.session_state.user_level = "Intermediate"
        elif ratio >= 0.2:
            st.session_state.user_level = "Elementary"
        else:
            st.session_state.user_level = "Beginner"
        st.session_state.xp += correct * 10
        st.session_state.step = 3
        st.experimental_rerun()

# ----------------------------------------------------
# STEP 3: Show Level, Generate Personalized Track
# ----------------------------------------------------
elif st.session_state.step == 3:
    st.header("Step 3: Results & Personalized Track")
    st.write(f"**Your level:** {st.session_state.user_level}")
    st.write(f"**XP:** {st.session_state.xp}")
    if st.button("Generate Learning Track"):
        track = generate_personalized_learning_track(st.session_state.main_topic, st.session_state.user_level)
        st.session_state.track = track
        st.session_state.step = 4
        st.experimental_rerun()

# ----------------------------------------------------
# STEP 4: Show Track, Start Final Assessment
# ----------------------------------------------------
elif st.session_state.step == 4:
    st.header("Step 4: Personalized Learning Track")
    st.write(st.session_state.get("track","[No track generated]"))
    if st.button("Start Final Assessment"):
        # final questions
        mix = (st.session_state.user_level != "Advanced")
        fq = generate_level_based_questions(st.session_state.main_topic, st.session_state.subtopics, st.session_state.user_level, mix_next_level=mix)
        st.session_state.final_questions = fq
        st.session_state.final_answers = [""]*len(fq)
        st.session_state.step = 5
        st.experimental_rerun()

# ----------------------------------------------------
# STEP 5: Final Assessment (Evaluation & Explanation in Table)
# ----------------------------------------------------
elif st.session_state.step == 5:
    st.header("Step 5: Final Assessment")
    # We will automatically do the evaluation after the user clicks "Finalize"
    for i, (lvl, sub, q) in enumerate(st.session_state.final_questions):
        st.write(f"**({lvl})** {sub} => {q}")
        st.session_state.final_answers[i] = st.text_area(f"Final Answer {i+1}", value=st.session_state.final_answers[i], key=f"fa_{i}")
    if st.button("Finalize Assessment"):
        # Build a results table
        data = []
        correct = 0
        total = len(st.session_state.final_questions)
        for i, (lvl, sub, q) in enumerate(st.session_state.final_questions):
            ans = st.session_state.final_answers[i].strip()
            if ans:
                eval_ = evaluate_answer(q, ans)
                expl_ = generate_explanation(q, ans)
                correct+=1
            else:
                eval_ = "No answer"
                expl_ = generate_personalized_tip(q, lvl)
            data.append({
                "Question": q,
                "YourAnswer": ans if ans else "[No Answer]",
                "Evaluation": eval_,
                "Explanation": expl_,
            })
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.write(f"You answered {correct} out of {total} questions.")
        ratio = correct/total if total else 0
        if ratio>0.7:
            st.success("You passed! Move up a level if you wish.")
            st.session_state.user_level = get_next_level(st.session_state.user_level)
            st.session_state.xp += correct*10
        # Let the user proceed to a new cycle or end
        if st.button("Restart from Step 1"):
            st.session_state.step = 1
            st.experimental_rerun()

# ----------------------------------------------------
# OPTIONAL: Download summary
# ----------------------------------------------------
def summary():
    s = f"Topic: {st.session_state.main_topic}\n"
    s += f"Subtopics: {', '.join(st.session_state.subtopics)}\n"
    s += f"Level: {st.session_state.user_level}\n"
    s += f"XP: {st.session_state.xp}\n"
    return s

st.download_button("Download Summary", summary(), file_name="summary.txt")
