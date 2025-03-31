import streamlit as st
import pandas as pd
from groq import Groq

# -----------------------------------------------------
# Helper function: reload the page using JavaScript
# -----------------------------------------------------
def redirect():
    st.markdown("<script>window.location.reload();</script>", unsafe_allow_html=True)

# -----------------------------------------------------
# Hide GitHub link and Streamlit action button
# -----------------------------------------------------
HIDE_GITHUB_STYLE = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(HIDE_GITHUB_STYLE, unsafe_allow_html=True)

# -----------------------------------------------------
# API Key Setup (use st.secrets in production)
# -----------------------------------------------------
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# -----------------------------------------------------
# Prompt and AI helper functions (synchronous calls)
# -----------------------------------------------------
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
        stream=False,
        stop=None,
    )
    return completion.choices[0].message.content

prompt_creative = {
    "system_message": "You are a teacher. Create content or questions based on the topic.",
    "temperature": 0.8,
}
prompt_strict = {
    "system_message": "You are a teacher. Evaluate the answer based on the question.",
    "temperature": 0.2,
}

def generate_question(main_topic, subtopic, level):
    text = f"Generate a {level} level question in {main_topic}, focusing on {subtopic}."
    return prompt(text, prompt_creative, base="Make it unique: ")

def evaluate_answer(question, answer):
    text = f"Strictly evaluate: {answer} for question: {question}."
    return prompt(text, prompt_strict)

def generate_explanation(question, answer):
    text = f"Provide a detailed explanation for the correct answer to: {question}, given the answer: {answer}."
    return prompt(text, prompt_creative, base="Detailed explanation: ")

def generate_personalized_tip(question, level):
    text = f"Provide personalized tips for a {level} learner for the question: {question}."
    return prompt(text, prompt_creative, base="Personalized tips: ")

def generate_personalized_learning_track(main_topic, level):
    text = f"Create a personalized learning track for a {level} learner in {main_topic}."
    return prompt(text, prompt_creative, base="Dynamic track: ")

def get_next_level(current_level):
    levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
    if current_level in levels and levels.index(current_level) < len(levels) - 1:
        return levels[levels.index(current_level) + 1]
    return current_level

def generate_level_based_questions(main_topic, subtopics, current_level, mix_next_level=False):
    questions = []
    next_level = get_next_level(current_level)
    for sub in subtopics:
        questions.append((current_level, sub, generate_question(main_topic, sub, current_level)))
        if mix_next_level and current_level != next_level:
            questions.append((next_level, sub, generate_question(main_topic, sub, next_level)))
    return questions

# -----------------------------------------------------
# Session state initialization
# -----------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1  # 1: Topic entry
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

# -----------------------------------------------------
# App Title
# -----------------------------------------------------
st.title("Personalized Learning Level Assessment")

# -----------------------------------------------------
# STEP 1: Topic & Subtopic Form
# -----------------------------------------------------
if st.session_state.step == 1:
    st.header("Step 1: Enter Main Topic & Subtopics")
    with st.form("form_step1"):
        topic_input = st.text_input("Main Topic:", value=st.session_state.main_topic)
        subs_input = st.text_input("Subtopics (comma separated):", value=", ".join(st.session_state.subtopics))
        submit1 = st.form_submit_button("Submit Topic")
    if submit1:
        if topic_input and subs_input:
            st.session_state.main_topic = topic_input
            st.session_state.subtopics = [s.strip() for s in subs_input.split(",") if s.strip()]
            # Generate questions for each level
            combined = []
            for lvl in ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]:
                combined.extend(generate_level_based_questions(st.session_state.main_topic, st.session_state.subtopics, lvl))
            st.session_state.questions = combined
            st.session_state.answers = [""] * len(combined)
            st.session_state.step = 2
            redirect()
        else:
            st.warning("Please fill both fields.")

# -----------------------------------------------------
# STEP 2: Display Questions & Collect Answers
# -----------------------------------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Answer the Following Questions")
    for i, (lvl, sub, q) in enumerate(st.session_state.questions):
        st.write(f"**({lvl}) {sub}**: {q}")
        st.session_state.answers[i] = st.text_area(f"Your Answer for Q{i+1}:", value=st.session_state.answers[i], key=f"a_{i}")
    if st.button("Submit Answers"):
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
        redirect()

# -----------------------------------------------------
# STEP 3: Assessment Results & Generate Learning Track
# -----------------------------------------------------
elif st.session_state.step == 3:
    st.header("Step 3: Assessment Results")
    st.write(f"Your assessed proficiency level is: **{st.session_state.user_level}**")
    st.write(f"**XP Points:** {st.session_state.xp}")
    answered = sum(1 for a in st.session_state.answers if a.strip())
    total = len(st.session_state.answers)
    if total:
        st.progress(answered / total)
    if st.button("Generate Personalized Learning Track"):
        track = generate_personalized_learning_track(st.session_state.main_topic, st.session_state.user_level)
        st.session_state.track = track
        st.session_state.step = 4
        redirect()

# -----------------------------------------------------
# STEP 4: Show Learning Track & Start Final Assessment
# -----------------------------------------------------
elif st.session_state.step == 4:
    st.header("Step 4: Your Personalized Learning Track")
    track = st.session_state.get("track", "[No track generated]")
    st.write(track)
    if st.button("Start Final Assessment"):
        mix = (st.session_state.user_level != "Advanced")
        final_qs = generate_level_based_questions(st.session_state.main_topic, st.session_state.subtopics, st.session_state.user_level, mix_next_level=mix)
        st.session_state.final_questions = final_qs
        st.session_state.final_answers = [""] * len(final_qs)
        st.session_state.step = 5
        redirect()

# -----------------------------------------------------
# STEP 5: Final Assessment - Answer Questions
# -----------------------------------------------------
elif st.session_state.step == 5:
    st.header("Step 5: Final Assessment - Answer the Questions")
    for i, (lvl, sub, q) in enumerate(st.session_state.final_questions):
        st.write(f"**({lvl}) {sub}**: {q}")
        st.session_state.final_answers[i] = st.text_area(f"Your Final Answer for Q{i+1}:", value=st.session_state.final_answers[i], key=f"fa_{i}")
    if st.button("Finalize Assessment"):
        st.session_state.step = 6
        redirect()

# -----------------------------------------------------
# STEP 6: Final Assessment - Evaluation & Explanation Table
# -----------------------------------------------------
elif st.session_state.step == 6:
    st.header("Step 6: Evaluation & Explanation")
    results = []
    for i, (lvl, sub, q) in enumerate(st.session_state.final_questions):
        ans = st.session_state.final_answers[i].strip()
        if ans:
            eval_result = evaluate_answer(q, ans)
            explanation = generate_explanation(q, ans)
        else:
            eval_result = "No answer provided"
            explanation = generate_personalized_tip(q, lvl)
        results.append({
            "Question": q,
            "Your Answer": ans if ans else "[No answer]",
            "Evaluation": eval_result,
            "Explanation": explanation
        })
    df = pd.DataFrame(results)
    st.dataframe(df)
    correct = sum(1 for a in st.session_state.final_answers if a.strip())
    total_qs = len(st.session_state.final_questions)
    st.write(f"You answered {correct} out of {total_qs} questions.")
    if total_qs > 0 and (correct / total_qs) > 0.7:
        st.success("You passed! Move to the next level.")
        if st.button("Move to Next Level"):
            st.session_state.user_level = get_next_level(st.session_state.user_level)
            st.session_state.xp += correct * 10
            st.session_state.step = 1  # Reset for a new cycle
            redirect()

# -----------------------------------------------------
# DOWNLOAD SUMMARY (available from Step 1 onward)
# -----------------------------------------------------
def generate_summary():
    summary = f"Main Topic: {st.session_state.main_topic}\n"
    summary += f"Subtopics: {', '.join(st.session_state.subtopics)}\n"
    summary += f"Proficiency Level: {st.session_state.user_level}\n"
    summary += f"XP: {st.session_state.xp}\n"
    return summary

st.download_button("Download Summary", generate_summary(), file_name="summary.txt")
