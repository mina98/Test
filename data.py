import streamlit as st
from groq import Groq

# Hide the GitHub link and the action button in Streamlit
hide_github_style = """
<style>
a[href="https://github.com/streamlit/streamlit"], .stActionButton {display: none;}
</style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

# Initialize the client (use your API key here)
client = Groq(api_key="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")

def prompt(text, base=''):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": base + text}],
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

def generate_question(main_topic, subtopic, level):
    """Generate a question dynamically based on the level, main topic, and subtopic."""
    prompt_text = f"Generate a {level} level question in {main_topic}, specifically focusing on {subtopic}. Make the question unique and appropriate for someone at the {level} level."
    question = prompt(text=main_topic, base=prompt_text)
    return question

def generate_level_based_questions(main_topic, subtopics):
    """Generate questions for different levels."""
    levels = ['Beginner', 'Elementary', 'Intermediate', 'Upper Intermediate', 'Advanced']
    questions = []
    for level in levels:
        for subtopic in subtopics:
            question = generate_question(main_topic, subtopic.strip(), level)
            questions.append((level, subtopic, question))
    return questions

def generate_feedback(question, answer):
    """Generate feedback for the user's answer using Groq API."""
    feedback_prompt = f"[question]\n{question}\n[Answer]\n{answer}"
    feedback = prompt(feedback_prompt, base="Give feedback on this answer.")
    return feedback

def generate_personalized_tip(question, level):
    """Generate a personalized learning suggestion based on user level and question."""
    tip_prompt = f"Generate personalized learning advice for {level} level based on this question: {question}"
    tip = prompt(text=tip_prompt, base="Provide personalized advice.")
    return tip

def generate_personalized_learning_track(main_topic, level):
    """Generate personalized learning track dynamically from Groq API."""
    track_prompt = f"Generate a personalized learning track for a {level} learner in the topic of {main_topic}."
    track = prompt(track_prompt, base="Provide a dynamic learning track.")
    return track

# Streamlit app layout
st.title('Personalized Learning Level Assessment')

# Initialize the session state to track the user's progress
if 'assessment_completed' not in st.session_state:
    st.session_state.assessment_completed = False

if 'questions_generated' not in st.session_state:
    st.session_state.questions_generated = False

if 'personalized_track_generated' not in st.session_state:
    st.session_state.personalized_track_generated = False

if 'loop_count' not in st.session_state:
    st.session_state.loop_count = 0  # Track the number of loops/iterations

# Step 1: If the assessment is not completed, show topic and subtopic inputs
if not st.session_state.assessment_completed:
    if st.session_state.loop_count == 0:
        # First loop iteration (initial input)
        st.header('Enter a Main Topic')
        user_main_topic = st.text_input("Enter a main topic you'd like to focus on (e.g., Math, Physics, Chemistry):")
        
        st.header('Enter Subtopics for Your Main Topic')
        user_subtopics = st.text_input("Enter subtopics for your main topic (comma separated):")
    else:
        # Subsequent loop iterations - keeping the same topic/subtopics
        user_main_topic = st.session_state.user_main_topic
        user_subtopics = st.session_state.user_subtopics_list
        st.write(f"Reassessing level based on previous session... Focusing on: {user_main_topic}")

    # Generate questions once the user submits the main topic and subtopics
    if (user_main_topic and user_subtopics) or st.session_state.loop_count > 0:
        if st.session_state.loop_count == 0:
            subtopics_list = [sub.strip() for sub in user_subtopics.split(',') if sub.strip()]
            st.session_state.user_subtopics_list = subtopics_list
        else:
            subtopics_list = st.session_state.user_subtopics_list

        st.write(f"Generating questions based on the main topic: {user_main_topic} and subtopics: {', '.join(subtopics_list)}")
        level_based_questions = generate_level_based_questions(user_main_topic, subtopics_list)

        st.session_state.level_based_questions = level_based_questions
        st.session_state.user_main_topic = user_main_topic
        st.session_state.answers = [""] * len(level_based_questions)
        st.session_state.questions_generated = True

# Step 2: Display the questions and collect answers once they are generated
if st.session_state.questions_generated and not st.session_state.assessment_completed:
    answers = st.session_state.answers
    for i, (level, subtopic, question) in enumerate(st.session_state.level_based_questions):
        st.write(f"{level.capitalize()} Level - {subtopic.capitalize()} Question {i + 1}: {question}")
        answers[i] = st.text_area(f"Your answer to {level.capitalize()} - {subtopic.capitalize()} Question {i + 1}", value=answers[i])

    if st.button('Submit Answers and Determine Level'):
        st.write("Thank you for your answers! Analyzing your level...")

        empty_answers = [ans for ans in answers if not ans.strip()]
        correct_answers = len([ans for ans in answers if ans.strip()])  # Count non-empty answers

        # Logic to determine the level based on answers
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

# Step 3: After the assessment, show the results and hide the input fields
if st.session_state.assessment_completed:
    st.write(f"Based on your answers, your proficiency level is: **{st.session_state.user_level}**")

    if st.button('Generate Personalized Learning Track'):
        user_level = st.session_state.user_level
        user_main_topic = st.session_state.user_main_topic

        # Generate personalized learning track dynamically
        personalized_track = generate_personalized_learning_track(user_main_topic, user_level)
        st.write(personalized_track)

        st.session_state.personalized_track_generated = True

# Step 4: Add an assessment for the personalized learning track
if st.session_state.personalized_track_generated:
    st.write("Now that you've studied the suggested topics, it's time for an assessment!")
    
    if st.button("Start Assessment"):
        assessment_questions = generate_level_based_questions(st.session_state.user_main_topic, st.session_state.user_subtopics_list)
        st.session_state.assessment_questions = assessment_questions
        st.session_state.assessment_answers = [""] * len(assessment_questions)

if 'assessment_questions' in st.session_state:
    st.write("Assessment: Answer the following questions based on your personalized learning track:")
    for i, (level, subtopic, question) in enumerate(st.session_state.assessment_questions):
        st.write(f"{level.capitalize()} Level - {subtopic.capitalize()} Question {i + 1}: {question}")
        st.session_state.assessment_answers[i] = st.text_area(f"Your answer to {level.capitalize()} - {subtopic.capitalize()} Question {i + 1}", value=st.session_state.assessment_answers[i])

    if st.button("Submit Assessment"):
        correct_answers = 0
        feedback_list = []
        total_questions = len(st.session_state.assessment_questions)

        # Generate feedback for each question and answer
        for i, (level, subtopic, question) in enumerate(st.session_state.assessment_questions):
            user_answer = st.session_state.assessment_answers[i].strip()
            if user_answer:
                feedback = generate_feedback(question, user_answer)
                feedback_list.append(f"Feedback for Question {i + 1}: {feedback}")
                correct_answers += 1
            else:
                tip = generate_personalized_tip(question, level)
                feedback_list.append(f"Question {i + 1} was not answered. Tip: {tip}")

        st.write(f"You answered {correct_answers} out of {total_questions} questions correctly!")
        
        for feedback in feedback_list:
            st.write(feedback)

        if correct_answers < total_questions:
            st.write("Consider revisiting the unanswered questions to improve your understanding.")

        # Reset the state and loop the process again for reassessment
        if st.button('Reassess Level and Continue'):
            st.session_state.assessment_completed = False
            st.session_state.questions_generated = False
            st.session_state.personalized_track_generated = False
            st.session_state.loop_count += 1
