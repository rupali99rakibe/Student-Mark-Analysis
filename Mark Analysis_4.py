import openai 
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Set your OpenAI API key
openai.api_key = "sk-jxHNeitHqQ7Q1hArkTo2XQkpG_JUU0fdpgiRuoebcZT3BlbkFJTbMHcXre_nSUrX6Jzesp8peW0DYtE8EN0Cnt3zelwA"
# Dictionary of study resources based on subject
study_resources = {
    "math": [
        "Khan Academy - https://www.khanacademy.org/math",
        "Paul’s Online Math Notes - http://tutorial.math.lamar.edu/",
        "Brilliant - https://www.brilliant.org"
    ],
    "science": [
        "CrashCourse Science - https://www.youtube.com/user/crashcourse",
        "NASA Science Resources - https://science.nasa.gov/",
        "Coursera Science Courses - https://www.coursera.org/browse/physical-science-and-engineering"
    ],
    "history": [
        "History.com - https://www.history.com/",
        "BBC Bitesize History - https://www.bbc.co.uk/bitesize/subjects/zxsfnbk",
        "World History Encyclopedia - https://www.worldhistory.org/"
    ],
    "english": [
        "Grammarly Blog - https://www.grammarly.com/blog/",
        "Purdue OWL - https://owl.purdue.edu/",
        "BBC Bitesize English - https://www.bbc.co.uk/bitesize/subjects/z3kw2hv"
    ],
    "general": [
        "Coursera - https://www.coursera.org/",
        "edX - https://www.edx.org/",
        "Khan Academy - https://www.khanacademy.org/"
    ]
}

def get_suggested_resources(question):
    """Detects subject keywords and returns recommended study resources."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["math", "algebra", "calculus", "geometry"]):
        return study_resources["math"]
    elif any(word in question_lower for word in ["science", "physics", "biology", "chemistry"]):
        return study_resources["science"]
    elif any(word in question_lower for word in ["history", "war", "civilization"]):
        return study_resources["history"]
    elif any(word in question_lower for word in ["english", "grammar", "literature"]):
        return study_resources["english"]
    else:
        return study_resources["general"]

def evaluate_response(question, user_answer, marks_type):
    try:
        # Detect the language
        try:
            detected_language = detect(question + " " + user_answer)
        except LangDetectException:
            detected_language = "en"

        # Marks categorization
        marks_mapping = {
            "1": "1-2", "2": "1-2", "3": "3-4", "4": "4-5", "5": "5-7", "6": "5-7", "7": "5-7", "10": "10"
        }
        normalized_marks_type = marks_mapping.get(marks_type, marks_type)

        # Evaluation instructions based on marks type
        instructions_map = {
            "1-2": "Evaluate the short answer for relevance and accuracy. Provide concise feedback.",
            "3-4": "Assess the explanation for clarity and completeness. Provide improvement suggestions.",
            "4-5": "Evaluate depth, clarity, and structure. Suggest missing details.",
            "5-7": "Check explanation depth, accuracy, and diagrams. Identify gaps and errors.",
            "10": "Assess structure, argument quality, and coherence. Provide detailed critique."
        }

        instructions = instructions_map.get(normalized_marks_type, "Invalid marks type.")
        if instructions == "Invalid marks type.":
            return "Invalid marks type. Please choose from 1-2, 3-4, 4-5, 5-7, or 10.", None, None

        # GPT-4 evaluation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": (
                    f"Question: {question}\n\n"
                    f"Student Answer: {user_answer}\n\n"
                    f"Total Marks: {marks_type}\n"
                    f"Provide awarded marks and feedback in {detected_language}."
                )}
            ],
            max_tokens=500
        )

        evaluation_text = response["choices"][0]["message"]["content"].strip()

        # Extract marks using regex
        marks_match = re.search(
            r'(?i)(?:marks\s*(awarded|given)?[:\-]?\s*|score\s*[:\-]?\s*)(\d+(\.\d+)?)\s*/\s*(\d+)', evaluation_text
        )
        awarded_marks = float(marks_match.group(2)) if marks_match else None
        total_marks = int(marks_match.group(4)) if marks_match else int(marks_type)

        # Provide resources if the marks are low
        if awarded_marks is not None and awarded_marks < (total_marks / 2):  
            suggested_resources = get_suggested_resources(question)
            evaluation_text += "\n\n**Suggested Study Resources:**\n" + "\n".join(suggested_resources)

        return evaluation_text, awarded_marks, total_marks

    except openai.OpenAIError as e:
        return f"An error occurred: {e}", None, None

if __name__ == "__main__":
    print("Welcome to the Exam Checker with Study Recommendations!")

    total_awarded_marks = 0
    total_possible_marks = 0

    while True:
        question = input("\nEnter the exam question: ")
        if question.lower() in ['exit', 'quit']:
            print(f"\nTotal Marks Awarded: {total_awarded_marks} / {total_possible_marks}")
            break

        print("Enter the student's answer (press Enter twice to finish):")
        student_answer_lines = []
        while True:
            line = input()
            if line == "":
                break
            student_answer_lines.append(line)
        user_answer = "\n".join(student_answer_lines)

        if not user_answer.strip():
            print("Answer cannot be empty. Please re-enter.")
            continue

        marks_type = input("Enter the marks for the question (1, 2, 3, ..., 7 or 10): ").strip()

        # Evaluate response
        evaluation, awarded_marks, total_marks = evaluate_response(question, user_answer, marks_type)

        print("\nEvaluation:")
        print(evaluation)

        if awarded_marks is not None and total_marks is not None:
            print(f"\nMarks: {awarded_marks}/{total_marks}")
            total_awarded_marks += awarded_marks
            total_possible_marks += total_marks
