import streamlit as st
from groq import Groq

# Hide the GitHub link and the action button in Streamlit
hide_github_style = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

# API key initialization (consider using st.secrets for production)
a = "gsk_9Pa"
c = "aXwe"
client = Groq(api_key=a + "x4HWcCgNRdhnZZusFWGdyb3FYvea7ZIQUdTuZJnvekqdO" + c)

# --------------------- AI Prompt Functions --------------------- #
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
    prompt_text = f"Generate a {level} level question in {main_topic}, specifically focusing on {subtopic}. Make the question unique and appropriate for someone at the {level} level."
    question = prompt(text=main_topic, prompt_type=prompt_creative, base=prompt_text)
    return question

def evaluate_answer(question, answer):
    prompt_text = f"Evaluate the following answer strictly: {answer} to the question: {question}. Do not provide hints, just the evaluation."
    evaluation = prompt(text=prompt_text, prompt_type=prompt_strict)
    return evaluation

def generate_tip(question, answer):
    tip_prompt = f"Provide helpful tips or hints to improve understanding of the following question: {question}. Avoid generating a full answer."
    tip = prompt(tip_prompt, prompt_type=prompt_creative, base="Provide tips only.")
    return tip

def generate_personalized_tip(question, level):
    tip_prompt = f"Provide personalized tips for a {level} level learner based on this question: {question}."
    tip = prompt(tip_prompt, prompt_type=prompt_creative, base="Provide personalized advice.")
    return tip

def generate_personalized_learning_track(main_topic, level):
    track_prompt = f"Generate a personalized learning track for a {level} learner in the topic of {main_topic}."
    track = prompt(track_prompt, prompt_type=prompt_creative, base="Provide a dynamic learning track.")
    return track

def generate_explanation(question, answer):
    explanation_prompt = {
        "system_message": "You are a teacher. Provide a detailed explanation of the correct answer.",
        "temperature": 0.3,
    }
    prompt_text = f"Give a thorough, step-by-step explanation for the correct answer to the question: {question}"
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

# --------------------- Session State Initialization --------------------- #
if 'assessment_completed' not in st.session_state:
    st.session_state.assessment_completed = False
if 'questions_generated' not in st.session_state:
    st.session_state.questions_generated = False
if 'personalized_track_generated' not in st.session_state:
    st.session_state.personalized_track_generated = False
if 'loop_count' not in st.session_state:
    st.session_state.loop_count = 0  # Count iterations
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = {}
if 'explanations' not in st.session_state:
    st.session_state.explanations = {}

# --------------------- App Title --------------------- #
st.title('Personalized Learning Level Assessment')

# --------------------- Demo Mode --------------------- #
if st.button("Try Demo Mode"):
    st.session_state.user_main_topic = "Math"
    st.session_state.user_subtopics_list = ["Algebra", "Geometry", "Calculus"]
    st.session_state.loop_count = 0
    st.stop()  # Halt execution; the updated session state will trigger a re-run.

# --------------------- Step 1: Input for Topic and Subtopics --------------------- #
if not st.session_state.assessment_completed:
    st.header('Enter a Main Topic')
    # Use the value from session state if it exists; otherwise, default to an empty string.
    user_main_topic = st.text_input(
        "Enter a main topic you'd like to focus on (e.g., Math, Physics, Chemistry):", 
        value=st.session_state.get("user_main_topic", "")
    )
    st.header('Enter Subtopics for Your Main Topic')
    user_subtopics = st.text_input(
        "Enter subtopics for your main topic (comma separated):", 
        value=", ".join(st.session_state.get("user_subtopics_list", []))
    )

    if user_main_topic and user_subtopics:
        # Update session state with current inputs
        st.session_state.user_main_topic = user_main_topic
        subtopics_list = [sub.strip() for sub in user_subtopics.split(',') if sub.strip()]
        st.session_state.user_subtopics_list = subtopics_list

        st.write(f"Generating questions based on the main topic: {user_main_topic} and subtopics: {', '.join(subtopics_list)}")
        
        # Generate questions for all levels for initial assessment
        level_based_questions = []
        levels = ['Beginner', 'Elementary', 'Intermediate', 'Upper Intermediate', 'Advanced']
        for level in levels:
            level_based_questions.extend(generate_level_based_questions(user_main_topic, subtopics_list, level))
        
        st.session_state.level_based_questions = level_based_questions
        st.session_state.answers = [""] * len(level_based_questions)
        st.session_state.questions_generated = True
        st.stop()  # Stop execution so that updated state is used on re-run

# --------------------- Step 2: Display Questions and Collect Answers --------------------- #
if st.session_state.questions_generated and not st.session_state.assessment_completed:
    st.header("Answer the following questions:")
    answers = st.session_state.answers
    for i, (level, subtopic, question) in enumerate(st.session_state.level_based_questions):
        st.write(f"**{level.capitalize()} Level - {subtopic.capitalize()} Question {i + 1}:** {question}")
        answers[i] = st.text_area(f"Your answer for Question {i + 1}", value=answers[i], key=f"ans_{i}")
    if st.button('Submit Answers and Determine Level'):
        st.write("Thank you for your answers! Analyzing your level...")
        empty_answers = [ans for ans in answers if not ans.strip()]
        correct_answers = len([ans for ans in answers if ans.strip()])
        # Determine level based on percentage of non-empty answers
        if len(empty_answers) == len(answers):
            user_level = 'Beginner'
        else:
            if correct_answers >= len(answers) * 0.8:
                user_level = 'Advanced'
            elif correct_answers >= len(answers) * 0.6:
                user_level = 'Upper Intermediate'
            elif correct_answers >= len(answers) * 0.4:
                user_level = 'Intermediate'
            elif correct_answers >= len(answers) * 0.2:
                user_level = 'Elementary'
            else:
                user_level = 'Beginner'
        
        st.session_state.user_level = user_level
        st.session_state.assessment_completed = True
        # Update XP points (e.g., 10 points per answered question)
        st.session_state.xp += correct_answers * 10
        st.stop()

# --------------------- Step 3: Display Assessment Results & Learning Track --------------------- #
if st.session_state.assessment_completed:
    st.header("Assessment Results")
    st.write(f"Based on your answers, your proficiency level is: **{st.session_state.user_level}**")
    st.write(f"**XP Points:** {st.session_state.xp}")
    st.progress(len([ans for ans in st.session_state.answers if ans.strip()]) / len(st.session_state.answers))
    
    if st.button('Generate Personalized Learning Track'):
        user_level = st.session_state.user_level
        user_main_topic = st.session_state.user_main_topic
        personalized_track = generate_personalized_learning_track(user_main_topic, user_level)
        st.write("### Your Personalized Learning Track:")
        st.write(personalized_track)
        st.session_state.personalized_track_generated = True
        st.stop()

# --------------------- Step 4: Final Assessment with Evaluation & Explanation --------------------- #
if st.session_state.personalized_track_generated:
    st.header("Final Assessment on Your Personalized Learning Track")
    if st.button("Start Assessment"):
        mix_next_level = False
        if st.session_state.user_level != 'Advanced':
            mix_next_level = True
        assessment_questions = generate_level_based_questions(
            st.session_state.user_main_topic,
            st.session_state.user_subtopics_list,
            st.session_state.user_level,
            mix_next_level=mix_next_level
        )
        st.session_state.assessment_questions = assessment_questions
        st.session_state.assessment_answers = [""] * len(assessment_questions)
        st.stop()

if 'assessment_questions' in st.session_state:
    st.subheader("Answer the following assessment questions:")
    for i, (level, subtopic, question) in enumerate(st.session_state.assessment_questions):
        st.write(f"**{level.capitalize()} Level - {subtopic.capitalize()} Question {i + 1}:** {question}")
        st.session_state.assessment_answers[i] = st.text_area(
            f"Your answer for Assessment Question {i + 1}", 
            value=st.session_state.assessment_answers[i],
            key=f"assess_ans_{i}"
        )
        # If an answer is provided, offer evaluation and explanation buttons
        if st.session_state.assessment_answers[i].strip():
            if st.button("Show Strict Evaluation", key=f"eval_{i}"):
                evaluation = evaluate_answer(question, st.session_state.assessment_answers[i])
                st.session_state.evaluations[i] = evaluation
            if st.session_state.evaluations.get(i):
                st.write(f"**Evaluation for Question {i+1}:** {st.session_state.evaluations[i]}")
            if st.button("Show Explanation", key=f"explain_{i}"):
                explanation = generate_explanation(question, st.session_state.assessment_answers[i])
                st.session_state.explanations[i] = explanation
            if st.session_state.explanations.get(i):
                st.write(f"**Explanation for Question {i+1}:** {st.session_state.explanations[i]}")
        else:
            tip = generate_personalized_tip(question, level)
            st.write(f"Question {i + 1} was not answered. Tip: {tip}")

    if st.button("Submit Final Assessment"):
        correct_answers = len([ans for ans in st.session_state.assessment_answers if ans.strip()])
        total_questions = len(st.session_state.assessment_questions)
        st.write(f"You answered {correct_answers} out of {total_questions} questions.")
        if correct_answers < total_questions:
            st.write("Consider revisiting the unanswered questions to improve your understanding.")
        if correct_answers / total_questions > 0.7:
            st.write("Congratulations! You've progressed to the next level.")
            if st.button("Move to the Next Level"):
                st.session_state.user_level = get_next_level(st.session_state.user_level)
                # Reset for a new loop/assessment cycle
                st.session_state.assessment_completed = False
                st.session_state.questions_generated = False
                st.session_state.personalized_track_generated = False
                st.session_state.loop_count += 1
                st.stop()

# --------------------- Optional: Download Progress Summary --------------------- #
def generate_summary():
    summary = f"Main Topic: {st.session_state.get('user_main_topic', '')}\n"
    summary += f"Subtopics: {', '.join(st.session_state.get('user_subtopics_list', []))}\n"
    summary += f"Proficiency Level: {st.session_state.get('user_level', '')}\n"
    summary += f"XP Points: {st.session_state.get('xp', 0)}\n"
    summary += "Assessment Answers:\n"
    for i, ans in enumerate(st.session_state.get('assessment_answers', [])):
        summary += f"Q{i+1}: {ans}\n"
    return summary

if st.session_state.get('user_level'):
    summary_str = generate_summary()
    st.download_button("Download Your Learning Summary", summary_str, file_name="learning_summary.txt")
