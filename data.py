import streamlit as st
from groq import Groq

# -------------------------------------------------------------------
#  Hide the GitHub link and the action button in Streamlit
# -------------------------------------------------------------------
hide_github_style = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

# -------------------------------------------------------------------
#  API key initialization (consider using st.secrets for production)
# -------------------------------------------------------------------
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# -------------------------------------------------------------------
#  AI Prompt Functions
# -------------------------------------------------------------------
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
                   f"Make the question unique and appropriate for someone at the {level} level.")
    question = prompt(text=main_topic, prompt_type=prompt_creative, base=prompt_text)
    return question

def evaluate_answer(question, answer):
    prompt_text = (f"Evaluate the following answer strictly: {answer} to the question: {question}. "
                   "Do not provide hints, just the evaluation.")
    evaluation = prompt(text=prompt_text, prompt_type=prompt_strict)
    return evaluation

def generate_tip(question, answer):
    tip_prompt = (f"Provide helpful tips or hints to improve understanding of the following question: {question}. "
                  f"Avoid generating a full answer.")
    tip = prompt(tip_prompt, prompt_type=prompt_creative, base="Provide tips only.")
    return tip

def generate_personalized_tip(question, level):
    tip_prompt = f"Provide personalized tips for a {level} level learner based on this question: {question}."
    tip = prompt(tip_prompt, prompt_type=prompt_creative, base="Provide personalized advice.")
    return tip

def generate_personalized_learning_track(main_topic, level):
    track_prompt = (f"Generate a personalized learning track for a {level} learner "
                    f"in the topic of {main_topic}.")
    track = prompt(track_prompt, prompt_type=prompt_creative, base="Provide a dynamic learning track.")
    return track

def generate_explanation(question, answer):
    explanation_prompt = {
        "system_message": "You are a teacher. Provide a detailed explanation of the correct answer.",
        "temperature": 0.3,
    }
    prompt_text = (f"Give a thorough, step-by-step explanation for the correct answer to the question: {question}")
    explanation = prompt(text=prompt_text, prompt_type=explanation_prompt, base="Detailed solution: ")
    return explanation

def get_next_level(current_level):
    levels = ['Beginner', 'Elementary', 'Intermediate', 'Upper Intermediate', 'Advanced']
    if current_level in levels and levels.index(current_level) < len(levels) - 1:
        return levels[levels.index(current_level) + 1]
    return current_level

def generate_level_based_questions(main_topic, subtopics, current_level, mix_next_level=False):
    levels = ['Beginner', 'Elementary', 'Intermediate', 'Upper Intermediate', 'Advanced']
    questions = []
    next_level = get_next_level(current_level)

    for subtopic in subtopics:
        questions.append((current_level, subtopic, generate_question(main_topic, subtopic.strip(), current_level)))
        if mix_next_level and current_level != next_level:
            questions.append((next_level, subtopic, generate_question(main_topic, subtopic.strip(), next_level)))
    return questions

# -------------------------------------------------------------------
#  Session State Initialization
# -------------------------------------------------------------------
# We'll store a "current_step" to keep track of which portion of the UI we show.
# Steps:
# 0 -> Start screen
# 1 -> Topic entry form
# 2 -> Display generated questions & collect answers
# 3 -> Show level results
# 4 -> Show personalized track
# 5 -> Final assessment question generation
# 6 -> Final assessment Q&A

if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

if 'user_main_topic' not in st.session_state:
    st.session_state.user_main_topic = ""
if 'user_subtopics_list' not in st.session_state:
    st.session_state.user_subtopics_list = []
if 'assessment_completed' not in st.session_state:
    st.session_state.assessment_completed = False
if 'personalized_track_generated' not in st.session_state:
    st.session_state.personalized_track_generated = False
if 'loop_count' not in st.session_state:
    st.session_state.loop_count = 0
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'user_level' not in st.session_state:
    st.session_state.user_level = 'Beginner'
if 'level_based_questions' not in st.session_state:
    st.session_state.level_based_questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'assessment_questions' not in st.session_state:
    st.session_state.assessment_questions = []
if 'assessment_answers' not in st.session_state:
    st.session_state.assessment_answers = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = {}
if 'explanations' not in st.session_state:
    st.session_state.explanations = {}

# -------------------------------------------------------------------
#  App Title
# -------------------------------------------------------------------
st.title('Personalized Learning Level Assessment')

# -------------------------------------------------------------------
#  Step 0: Start Screen
# -------------------------------------------------------------------
if st.session_state.current_step == 0:
    st.write("Welcome to the AI-Powered Personalized Learning app!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Demo Mode"):
            # Pre-fill some demo data
            st.session_state.user_main_topic = "Math"
            st.session_state.user_subtopics_list = ["Algebra", "Geometry", "Calculus"]
            st.session_state.current_step = 1
            st.stop()
    with col2:
        if st.button("Start from Scratch"):
            # Clear previous data
            st.session_state.user_main_topic = ""
            st.session_state.user_subtopics_list = []
            st.session_state.current_step = 1
            st.stop()

# -------------------------------------------------------------------
#  Step 1: Topic and Subtopic Form
# -------------------------------------------------------------------
if st.session_state.current_step == 1:
    st.header("Step 1: Enter Main Topic & Subtopics")
    with st.form(key="topic_form"):
        user_main_topic = st.text_input(
            "Enter a main topic you'd like to focus on (e.g., Math, Physics, Chemistry):",
            value=st.session_state.user_main_topic
        )
        user_subtopics = st.text_input(
            "Enter subtopics for your main topic (comma separated):",
            value=", ".join(st.session_state.user_subtopics_list)
        )
        submit_topic = st.form_submit_button("Submit Topic")

    if submit_topic:
        if user_main_topic and user_subtopics:
            st.session_state.user_main_topic = user_main_topic
            subtopics_list = [sub.strip() for sub in user_subtopics.split(',') if sub.strip()]
            st.session_state.user_subtopics_list = subtopics_list

            # Generate questions for all levels for the initial assessment
            level_based_questions = []
            levels = ['Beginner', 'Elementary', 'Intermediate', 'Upper Intermediate', 'Advanced']
            for lvl in levels:
                level_based_questions.extend(generate_level_based_questions(
                    user_main_topic,
                    subtopics_list,
                    lvl
                ))

            st.session_state.level_based_questions = level_based_questions
            st.session_state.answers = [""] * len(level_based_questions)

            # Move to Step 2
            st.session_state.current_step = 2
            st.stop()
        else:
            st.warning("Please provide both a main topic and at least one subtopic before submitting.")

# -------------------------------------------------------------------
#  Step 2: Display Generated Questions & Collect Answers
# -------------------------------------------------------------------
if st.session_state.current_step == 2:
    st.header("Step 2: Answer the Following Questions")
    answers = st.session_state.answers
    for i, (level, subtopic, question) in enumerate(st.session_state.level_based_questions):
        st.write(f"**{level.capitalize()} - {subtopic.capitalize()} - Q{i+1}:** {question}")
        answers[i] = st.text_area(f"Your Answer to Q{i+1}:", value=answers[i], key=f"answer_{i}")

    if st.button("Submit Answers & Determine Level"):
        empty_answers = [ans for ans in answers if not ans.strip()]
        correct_answers = len([ans for ans in answers if ans.strip()])
        # Very basic "evaluation" for demonstration
        if len(empty_answers) == len(answers):
            user_level = 'Beginner'
        else:
            total_qs = len(answers)
            if correct_answers >= total_qs * 0.8:
                user_level = 'Advanced'
            elif correct_answers >= total_qs * 0.6:
                user_level = 'Upper Intermediate'
            elif correct_answers >= total_qs * 0.4:
                user_level = 'Intermediate'
            elif correct_answers >= total_qs * 0.2:
                user_level = 'Elementary'
            else:
                user_level = 'Beginner'

        st.session_state.user_level = user_level
        st.session_state.xp += correct_answers * 10
        st.session_state.current_step = 3
        st.stop()

# -------------------------------------------------------------------
#  Step 3: Show Results & Option to Generate Personalized Track
# -------------------------------------------------------------------
if st.session_state.current_step == 3:
    st.header("Step 3: Assessment Results")
    st.write(f"Based on your answers, your proficiency level is: **{st.session_state.user_level}**")
    st.write(f"**XP Points:** {st.session_state.xp}")

    # Show a progress bar for how many questions were answered
    answered_count = sum(1 for ans in st.session_state.answers if ans.strip())
    total_count = len(st.session_state.answers)
    progress_ratio = answered_count / total_count if total_count else 0
    st.progress(progress_ratio)

    if st.button("Generate Personalized Learning Track"):
        # Generate track
        track = generate_personalized_learning_track(
            st.session_state.user_main_topic,
            st.session_state.user_level
        )
        st.session_state.personalized_track = track
        st.session_state.current_step = 4
        st.stop()

# -------------------------------------------------------------------
#  Step 4: Show Personalized Learning Track & Option to Start Final Assessment
# -------------------------------------------------------------------
if st.session_state.current_step == 4:
    st.header("Step 4: Your Personalized Learning Track")
    personalized_track = st.session_state.get("personalized_track", "")
    if personalized_track:
        st.write(personalized_track)
    else:
        st.write("No personalized track generated yet.")

    if st.button("Start Final Assessment"):
        # Generate final assessment questions
        mix_next_level = (st.session_state.user_level != 'Advanced')
        final_questions = generate_level_based_questions(
            st.session_state.user_main_topic,
            st.session_state.user_subtopics_list,
            st.session_state.user_level,
            mix_next_level=mix_next_level
        )
        st.session_state.assessment_questions = final_questions
        st.session_state.assessment_answers = [""] * len(final_questions)
        st.session_state.current_step = 5
        st.stop()

# -------------------------------------------------------------------
#  Step 5: Final Assessment Q&A
# -------------------------------------------------------------------
if st.session_state.current_step == 5:
    st.header("Step 5: Final Assessment - Questions")
    for i, (level, subtopic, question) in enumerate(st.session_state.assessment_questions):
        st.write(f"**{level.capitalize()} - {subtopic.capitalize()} - Q{i+1}:** {question}")
        st.session_state.assessment_answers[i] = st.text_area(
            f"Your Answer to Final Q{i+1}:",
            value=st.session_state.assessment_answers[i],
            key=f"final_ans_{i}"
        )
    if st.button("Submit Final Assessment"):
        st.session_state.current_step = 6
        st.stop()

# -------------------------------------------------------------------
#  Step 6: Final Assessment - Evaluation & Explanation
# -------------------------------------------------------------------
if st.session_state.current_step == 6:
    st.header("Step 6: Final Assessment - Evaluation & Explanation")

    correct_answers = 0
    total_questions = len(st.session_state.assessment_questions)

    # We'll show each question, answer, plus buttons for evaluation/explanation
    for i, (level, subtopic, question) in enumerate(st.session_state.assessment_questions):
        answer = st.session_state.assessment_answers[i].strip()
        st.write(f"### Q{i+1} - {level.capitalize()} {subtopic.capitalize()}")
        st.write(f"**Your Answer**: {answer or '[No answer given]'}")

        if answer:
            # Offer Strict Evaluation
            if st.button(f"Strict Evaluation Q{i+1}", key=f"eval_btn_{i}"):
                eval_result = evaluate_answer(question, answer)
                st.session_state.evaluations[i] = eval_result
                st.stop()
            if st.session_state.evaluations.get(i):
                st.write(f"**Evaluation**: {st.session_state.evaluations[i]}")

            # Offer Explanation
            if st.button(f"Show Explanation Q{i+1}", key=f"explain_btn_{i}"):
                exp_result = generate_explanation(question, answer)
                st.session_state.explanations[i] = exp_result
                st.stop()
            if st.session_state.explanations.get(i):
                st.write(f"**Explanation**: {st.session_state.explanations[i]}")

            # Simple logic to count "correct" if not empty
            correct_answers += 1
        else:
            # If no answer, show a tip
            tip_msg = generate_personalized_tip(question, level)
            st.write(f"**Tip**: {tip_msg}")

    st.write(f"You answered {correct_answers} out of {total_questions} questions.")
    if total_questions > 0 and (correct_answers / total_questions) > 0.7:
        st.write("Congratulations! You've progressed to the next level.")
        if st.button("Move to Next Level"):
            st.session_state.user_level = get_next_level(st.session_state.user_level)
            # Reset steps to re-start
            st.session_state.current_step = 0
            st.session_state.loop_count += 1
            st.stop()

# -------------------------------------------------------------------
#  Optional: Download Progress Summary
# -------------------------------------------------------------------
def generate_summary():
    summary = f"Main Topic: {st.session_state.get('user_main_topic', '')}\n"
    summary += f"Subtopics: {', '.join(st.session_state.get('user_subtopics_list', []))}\n"
    summary += f"Proficiency Level: {st.session_state.get('user_level', '')}\n"
    summary += f"XP Points: {st.session_state.get('xp', 0)}\n"
    summary += "Assessment Answers (Final):\n"
    for i, ans in enumerate(st.session_state.get('assessment_answers', [])):
        summary += f"Q{i+1}: {ans}\n"
    return summary

if st.session_state.current_step >= 1:
    summary_str = generate_summary()
    st.download_button("Download Your Learning Summary", summary_str, file_name="learning_summary.txt")
