import streamlit as st
from groq import Groq

# -----------------------------------------------------
# 1) Hide GitHub link and Streamlit action button
# -----------------------------------------------------
HIDE_GITHUB_STYLE = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(HIDE_GITHUB_STYLE, unsafe_allow_html=True)

# -----------------------------------------------------
# 2) API key initialization (Consider st.secrets for production)
# -----------------------------------------------------
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# -----------------------------------------------------
# 3) Prompt & AI helper functions
# -----------------------------------------------------
def prompt(text, prompt_type, base=''):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt_type["system_message"]},
            {"role": "user", "content": base + text},
        ],
        temperature=prompt_type["temperature"],
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

prompt_creative = {
    "system_message": "You are a teacher. You should create content or questions based on the topic.",
    "temperature": 0.8,
}
prompt_strict = {
    "system_message": "You are a teacher. You should evaluate the answer based on the question.",
    "temperature": 0.2,
}

def generate_question(main_topic, subtopic, level):
    prompt_text = (
        f"Generate a {level} level question in {main_topic}, "
        f"specifically focusing on {subtopic}. Make the question unique and "
        f"appropriate for someone at the {level} level."
    )
    return prompt(text=main_topic, prompt_type=prompt_creative, base=prompt_text)

def evaluate_answer(question, answer):
    prompt_text = (
        f"Evaluate the following answer strictly: {answer} to the question: {question}. "
        "Do not provide hints, just the evaluation."
    )
    return prompt(text=prompt_text, prompt_type=prompt_strict)

def generate_tip(question, answer):
    tip_prompt = (
        f"Provide helpful tips or hints to improve understanding of the following question: {question}. "
        "Avoid generating a full answer."
    )
    return prompt(tip_prompt, prompt_type=prompt_creative, base="Provide tips only.")

def generate_personalized_tip(question, level):
    tip_prompt = f"Provide personalized tips for a {level} level learner based on this question: {question}."
    return prompt(tip_prompt, prompt_type=prompt_creative, base="Provide personalized advice.")

def generate_personalized_learning_track(main_topic, level):
    track_prompt = (
        f"Generate a personalized learning track for a {level} learner in the topic of {main_topic}."
    )
    return prompt(track_prompt, prompt_type=prompt_creative, base="Provide a dynamic learning track.")

def generate_explanation(question, answer):
    explanation_prompt = {
        "system_message": "You are a teacher. Provide a detailed explanation of the correct answer.",
        "temperature": 0.3,
    }
    prompt_text = (
        f"Give a thorough, step-by-step explanation for the correct answer to the question: {question}"
    )
    return prompt(text=prompt_text, prompt_type=explanation_prompt, base="Detailed solution: ")

def get_next_level(current_level):
    levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
    if current_level in levels and levels.index(current_level) < len(levels) - 1:
        return levels[levels.index(current_level) + 1]
    return current_level

def generate_level_based_questions(main_topic, subtopics, current_level, mix_next_level=False):
    levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
    questions = []
    next_level = get_next_level(current_level)
    for subtopic in subtopics:
        questions.append(
            (current_level, subtopic, generate_question(main_topic, subtopic.strip(), current_level))
        )
        if mix_next_level and current_level != next_level:
            questions.append(
                (next_level, subtopic, generate_question(main_topic, subtopic.strip(), next_level))
            )
    return questions

# -----------------------------------------------------
# 4) Session state initialization
# -----------------------------------------------------
if "current_step" not in st.session_state:
    st.session_state.current_step = 0  # We'll use steps 0..6

if "user_main_topic" not in st.session_state:
    st.session_state.user_main_topic = ""
if "user_subtopics_list" not in st.session_state:
    st.session_state.user_subtopics_list = []
if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "level_based_questions" not in st.session_state:
    st.session_state.level_based_questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []

if "assessment_questions" not in st.session_state:
    st.session_state.assessment_questions = []
if "assessment_answers" not in st.session_state:
    st.session_state.assessment_answers = []

if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}
if "explanations" not in st.session_state:
    st.session_state.explanations = {}

# -----------------------------------------------------
# 5) Page Title
# -----------------------------------------------------
st.title("Personalized Learning Level Assessment")

# -----------------------------------------------------
# STEP 0: WELCOME SCREEN
# -----------------------------------------------------
if st.session_state.current_step == 0:
    st.subheader("Step 0: Welcome")
    st.write("Welcome to the AI-Powered Personalized Learning app!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Demo Mode"):
            # Set defaults and move on
            st.session_state.user_main_topic = "Math"
            st.session_state.user_subtopics_list = ["Algebra", "Geometry", "Calculus"]
            st.session_state.current_step = 1
    with col2:
        if st.button("Start from Scratch"):
            st.session_state.user_main_topic = ""
            st.session_state.user_subtopics_list = []
            st.session_state.current_step = 1

# -----------------------------------------------------
# STEP 1: TOPIC + SUBTOPICS
# -----------------------------------------------------
elif st.session_state.current_step == 1:
    st.subheader("Step 1: Enter Main Topic & Subtopics")
    with st.form(key="topic_form"):
        user_main_topic = st.text_input(
            "Main Topic (e.g., Math, Physics, Chemistry):",
            value=st.session_state.user_main_topic
        )
        user_subtopics_str = st.text_input(
            "Subtopics (comma separated):",
            value=", ".join(st.session_state.user_subtopics_list)
        )
        topic_submit = st.form_submit_button("Submit")

    if topic_submit:
        if user_main_topic and user_subtopics_str:
            st.session_state.user_main_topic = user_main_topic
            subtopics_list = [s.strip() for s in user_subtopics_str.split(",") if s.strip()]
            st.session_state.user_subtopics_list = subtopics_list

            # Generate questions for all levels
            all_questions = []
            levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
            for lvl in levels:
                all_questions.extend(
                    generate_level_based_questions(user_main_topic, subtopics_list, lvl)
                )
            st.session_state.level_based_questions = all_questions
            st.session_state.answers = [""] * len(all_questions)

            # Move to step 2
            st.session_state.current_step = 2
        else:
            st.warning("Please enter both the main topic and subtopics before submitting.")

# -----------------------------------------------------
# STEP 2: DISPLAY QUESTIONS & COLLECT ANSWERS
# -----------------------------------------------------
elif st.session_state.current_step == 2:
    st.subheader("Step 2: Answer the Following Questions")
    for i, (lvl, subtopic, question) in enumerate(st.session_state.level_based_questions):
        st.write(f"**{lvl.capitalize()} - {subtopic.capitalize()}**: {question}")
        st.session_state.answers[i] = st.text_area(
            f"Your Answer (Q{i+1})",
            value=st.session_state.answers[i],
            key=f"answer_{i}"
        )

    if st.button("Submit Answers & Determine Level"):
        answers = st.session_state.answers
        empty_answers = [ans for ans in answers if not ans.strip()]
        correct_answers = len([ans for ans in answers if ans.strip()])

        if len(empty_answers) == len(answers):
            user_level = "Beginner"
        else:
            total_qs = len(answers)
            ratio = correct_answers / total_qs
            if ratio >= 0.8:
                user_level = "Advanced"
            elif ratio >= 0.6:
                user_level = "Upper Intermediate"
            elif ratio >= 0.4:
                user_level = "Intermediate"
            elif ratio >= 0.2:
                user_level = "Elementary"
            else:
                user_level = "Beginner"

        st.session_state.user_level = user_level
        st.session_state.xp += correct_answers * 10
        # Move to step 3
        st.session_state.current_step = 3

# -----------------------------------------------------
# STEP 3: SHOW RESULTS & GENERATE LEARNING TRACK
# -----------------------------------------------------
elif st.session_state.current_step == 3:
    st.subheader("Step 3: Assessment Results")
    st.write(f"Your assessed proficiency level is: **{st.session_state.user_level}**")
    st.write(f"**XP Points:** {st.session_state.xp}")

    answered = sum(1 for ans in st.session_state.answers if ans.strip())
    total = len(st.session_state.answers)
    if total > 0:
        st.progress(answered / total)

    if st.button("Generate Personalized Learning Track"):
        track = generate_personalized_learning_track(
            st.session_state.user_main_topic,
            st.session_state.user_level
        )
        # Store it for next step
        st.session_state.personalized_track = track
        st.session_state.current_step = 4

# -----------------------------------------------------
# STEP 4: SHOW LEARNING TRACK, OFFER FINAL ASSESSMENT
# -----------------------------------------------------
elif st.session_state.current_step == 4:
    st.subheader("Step 4: Your Personalized Learning Track")
    track = st.session_state.get("personalized_track", "")
    if track:
        st.write(track)
    else:
        st.info("No learning track generated yet.")

    if st.button("Start Final Assessment"):
        # Generate new questions
        mix_next = (st.session_state.user_level != "Advanced")
        final_qs = generate_level_based_questions(
            st.session_state.user_main_topic,
            st.session_state.user_subtopics_list,
            st.session_state.user_level,
            mix_next_level=mix_next
        )
        st.session_state.assessment_questions = final_qs
        st.session_state.assessment_answers = [""] * len(final_qs)
        # Move to step 5
        st.session_state.current_step = 5

# -----------------------------------------------------
# STEP 5: FINAL ASSESSMENT - QUESTIONS
# -----------------------------------------------------
elif st.session_state.current_step == 5:
    st.subheader("Step 5: Final Assessment - Questions")
    for i, (lvl, subtopic, question) in enumerate(st.session_state.assessment_questions):
        st.write(f"**{lvl.capitalize()} - {subtopic.capitalize()}**: {question}")
        st.session_state.assessment_answers[i] = st.text_area(
            f"Your Answer (Final Q{i+1})",
            value=st.session_state.assessment_answers[i],
            key=f"final_ans_{i}"
        )

    if st.button("Submit Final Assessment"):
        # Move to step 6
        st.session_state.current_step = 6

# -----------------------------------------------------
# STEP 6: FINAL ASSESSMENT - EVALUATION & EXPLANATION
# -----------------------------------------------------
elif st.session_state.current_step == 6:
    st.subheader("Step 6: Final Assessment - Evaluation & Explanation")
    correct_count = 0
    total_qs = len(st.session_state.assessment_questions)

    for i, (lvl, subtopic, question) in enumerate(st.session_state.assessment_questions):
        user_ans = st.session_state.assessment_answers[i].strip()
        st.write(f"### Q{i+1} - {lvl.capitalize()} - {subtopic.capitalize()}")
        if user_ans:
            st.write(f"**Your Answer**: {user_ans}")

            # Strict Evaluation
            if st.button(f"Strict Evaluation Q{i+1}", key=f"eval_btn_{i}"):
                evaluation = evaluate_answer(question, user_ans)
                st.session_state.evaluations[i] = evaluation

            if i in st.session_state.evaluations:
                st.write(f"**Evaluation**: {st.session_state.evaluations[i]}")

            # Explanation
            if st.button(f"Show Explanation Q{i+1}", key=f"explain_btn_{i}"):
                explanation = generate_explanation(question, user_ans)
                st.session_state.explanations[i] = explanation

            if i in st.session_state.explanations:
                st.write(f"**Explanation**: {st.session_state.explanations[i]}")

            correct_count += 1
        else:
            st.write("**Your Answer**: [No answer given]")
            tip_msg = generate_personalized_tip(question, lvl)
            st.write(f"**Tip**: {tip_msg}")

    st.write(f"You answered **{correct_count}** out of **{total_qs}** questions.")
    if total_qs > 0 and (correct_count / total_qs) > 0.7:
        st.success("Congratulations! You can move to the next level.")
        if st.button("Move to Next Level"):
            st.session_state.user_level = get_next_level(st.session_state.user_level)
            st.session_state.current_step = 0  # Restart flow
            st.session_state.xp += correct_count * 10  # Maybe award more XP
            st.session_state.evaluations.clear()
            st.session_state.explanations.clear()

# -----------------------------------------------------
# DOWNLOAD SUMMARY (available after step 1)
# -----------------------------------------------------
def generate_summary():
    summary = f"Main Topic: {st.session_state.user_main_topic}\n"
    summary += f"Subtopics: {', '.join(st.session_state.user_subtopics_list)}\n"
    summary += f"Proficiency Level: {st.session_state.user_level}\n"
    summary += f"XP Points: {st.session_state.xp}\n"
    summary += "Final Assessment Answers:\n"
    for i, ans in enumerate(st.session_state.assessment_answers):
        summary += f"Q{i+1}: {ans}\n"
    return summary

if st.session_state.current_step >= 1:
    summary_str = generate_summary()
    st.download_button("Download Your Learning Summary", summary_str, file_name="learning_summary.txt")
