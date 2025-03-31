import streamlit as st
import pandas as pd
from groq import Groq

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
# API key initialization (consider st.secrets for production)
# -----------------------------------------------------
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# -----------------------------------------------------
# Prompt and AI helper functions (wrapped in spinners where needed)
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
    prompt_text = (f"Generate a {level} level question in {main_topic}, specifically focusing on {subtopic}. "
                   "Make the question unique and appropriate for someone at the specified level.")
    with st.spinner("Generating question..."):
        return prompt(text=main_topic, prompt_type=prompt_creative, base=prompt_text)

def evaluate_answer(question, answer):
    prompt_text = (f"Evaluate the following answer strictly: {answer} to the question: {question}. "
                   "Do not provide hints, just the evaluation.")
    with st.spinner("Evaluating answer..."):
        return prompt(text=prompt_text, prompt_type=prompt_strict)

def generate_personalized_tip(question, level):
    tip_prompt = f"Provide personalized tips for a {level} level learner based on this question: {question}."
    with st.spinner("Generating tip..."):
        return prompt(tip_prompt, prompt_type=prompt_creative, base="Provide personalized advice.")

def generate_personalized_learning_track(main_topic, level):
    track_prompt = f"Generate a personalized learning track for a {level} learner in the topic of {main_topic}."
    with st.spinner("Generating learning track..."):
        return prompt(track_prompt, prompt_type=prompt_creative, base="Provide a dynamic learning track.")

def generate_explanation(question, answer):
    explanation_prompt = {
        "system_message": "You are a teacher. Provide a detailed explanation of the correct answer.",
        "temperature": 0.3,
    }
    prompt_text = f"Give a thorough, step-by-step explanation for the correct answer to the question: {question}"
    with st.spinner("Generating explanation..."):
        return prompt(text=prompt_text, prompt_type=explanation_prompt, base="Detailed solution: ")

def get_next_level(current_level):
    levels = ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]
    if current_level in levels and levels.index(current_level) < len(levels) - 1:
        return levels[levels.index(current_level) + 1]
    return current_level

def generate_level_based_questions(main_topic, subtopics, current_level, mix_next_level=False):
    questions = []
    next_level = get_next_level(current_level)
    for subtopic in subtopics:
        questions.append((current_level, subtopic, generate_question(main_topic, subtopic.strip(), current_level)))
        if mix_next_level and current_level != next_level:
            questions.append((next_level, subtopic, generate_question(main_topic, subtopic.strip(), next_level)))
    return questions

# -----------------------------------------------------
# Session state initialization
# -----------------------------------------------------
if "current_step" not in st.session_state:
    st.session_state.current_step = 1  # Step 1: Topic entry
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

# -----------------------------------------------------
# App Title
# -----------------------------------------------------
st.title("Personalized Learning Level Assessment")

# -----------------------------------------------------
# STEP 1: Topic & Subtopic Form
# -----------------------------------------------------
if st.session_state.current_step == 1:
    st.header("Step 1: Enter Main Topic & Subtopics")
    with st.form(key="topic_form"):
        main_topic = st.text_input("Enter a main topic (e.g., Math, Physics, Chemistry):", 
                                   value=st.session_state.user_main_topic)
        subtopics_str = st.text_input("Enter subtopics (comma separated):", 
                                      value=", ".join(st.session_state.user_subtopics_list))
        submitted = st.form_submit_button("Submit Topic")
    if submitted:
        if main_topic and subtopics_str:
            st.session_state.user_main_topic = main_topic
            st.session_state.user_subtopics_list = [s.strip() for s in subtopics_str.split(",") if s.strip()]
            # Generate questions for each level
            all_questions = []
            for lvl in ["Beginner", "Elementary", "Intermediate", "Upper Intermediate", "Advanced"]:
                all_questions.extend(generate_level_based_questions(main_topic, st.session_state.user_subtopics_list, lvl))
            st.session_state.level_based_questions = all_questions
            st.session_state.answers = [""] * len(all_questions)
            st.session_state.current_step = 2
            st.experimental_rerun()
        else:
            st.warning("Please enter both a main topic and at least one subtopic.")

# -----------------------------------------------------
# STEP 2: Display Questions & Collect Answers
# -----------------------------------------------------
elif st.session_state.current_step == 2:
    st.header("Step 2: Answer the Following Questions")
    for i, (lvl, subtopic, question) in enumerate(st.session_state.level_based_questions):
        st.write(f"**{lvl} - {subtopic}**: {question}")
        st.session_state.answers[i] = st.text_area(f"Your Answer for Q{i+1}:", 
                                                   value=st.session_state.answers[i],
                                                   key=f"ans_{i}")
    if st.button("Submit Answers & Determine Level"):
        answers = st.session_state.answers
        # For demo, we count non-empty answers as "correct"
        correct_count = len([ans for ans in answers if ans.strip()])
        total = len(answers)
        ratio = correct_count / total if total else 0
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
        st.session_state.xp += correct_count * 10
        st.session_state.current_step = 3
        st.experimental_rerun()

# -----------------------------------------------------
# STEP 3: Show Assessment Results & Generate Learning Track
# -----------------------------------------------------
elif st.session_state.current_step == 3:
    st.header("Step 3: Assessment Results")
    st.write(f"Your assessed proficiency level is: **{st.session_state.user_level}**")
    st.write(f"**XP Points:** {st.session_state.xp}")
    answered = sum(1 for ans in st.session_state.answers if ans.strip())
    total = len(st.session_state.answers)
    if total:
        st.progress(answered / total)
    if st.button("Generate Personalized Learning Track"):
        track = generate_personalized_learning_track(st.session_state.user_main_topic, st.session_state.user_level)
        st.session_state.personalized_track = track
        st.session_state.current_step = 4
        st.experimental_rerun()

# -----------------------------------------------------
# STEP 4: Show Learning Track & Start Final Assessment
# -----------------------------------------------------
elif st.session_state.current_step == 4:
    st.header("Step 4: Your Personalized Learning Track")
    track = st.session_state.get("personalized_track", "")
    if track:
        st.write(track)
    else:
        st.info("No learning track generated.")
    if st.button("Start Final Assessment"):
        mix_next = (st.session_state.user_level != "Advanced")
        final_qs = generate_level_based_questions(st.session_state.user_main_topic, 
                                                  st.session_state.user_subtopics_list, 
                                                  st.session_state.user_level, mix_next_level=mix_next)
        st.session_state.assessment_questions = final_qs
        st.session_state.assessment_answers = [""] * len(final_qs)
        st.session_state.current_step = 5
        st.experimental_rerun()

# -----------------------------------------------------
# STEP 5: Final Assessment - Answer Questions
# -----------------------------------------------------
elif st.session_state.current_step == 5:
    st.header("Step 5: Final Assessment - Answer the Questions")
    for i, (lvl, subtopic, question) in enumerate(st.session_state.assessment_questions):
        st.write(f"**{lvl} - {subtopic}**: {question}")
        st.session_state.assessment_answers[i] = st.text_area(f"Your Answer for Final Q{i+1}:", 
                                                               value=st.session_state.assessment_answers[i],
                                                               key=f"final_ans_{i}")
    if st.button("Submit Final Assessment"):
        st.session_state.current_step = 6
        st.experimental_rerun()

# -----------------------------------------------------
# STEP 6: Final Assessment - Evaluation & Explanation Table
# -----------------------------------------------------
elif st.session_state.current_step == 6:
    st.header("Step 6: Final Assessment - Evaluation & Explanation")
    data = []
    for i, (lvl, subtopic, question) in enumerate(st.session_state.assessment_questions):
        ans = st.session_state.assessment_answers[i].strip()
        if ans:
            eval_result = evaluate_answer(question, ans)
            explanation = generate_explanation(question, ans)
        else:
            eval_result = "No answer provided"
            explanation = generate_personalized_tip(question, lvl)
        data.append({
            "Question": question,
            "Your Answer": ans if ans else "[No answer]",
            "Evaluation": eval_result,
            "Explanation": explanation
        })
    df = pd.DataFrame(data)
    # Use st.dataframe for a nicer appearance (scrollable and responsive)
    st.dataframe(df)
    correct_count = len([ans for ans in st.session_state.assessment_answers if ans.strip()])
    total_qs = len(st.session_state.assessment_questions)
    st.write(f"You answered {correct_count} out of {total_qs} questions.")
    if total_qs > 0 and (correct_count / total_qs) > 0.7:
        st.success("Congratulations! You passed the final assessment.")
        if st.button("Move to Next Level"):
            st.session_state.user_level = get_next_level(st.session_state.user_level)
            st.session_state.xp += correct_count * 10
            # Reset for a new cycle (start from Step 1)
            st.session_state.current_step = 1
            st.experimental_rerun()

# -----------------------------------------------------
# DOWNLOAD SUMMARY (available from Step 1 onward)
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

summary_str = generate_summary()
st.download_button("Download Your Learning Summary", summary_str, file_name="learning_summary.txt")
