import openai
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Set your OpenAI API key
openai.api_key = "sk-jxHNeitHqQ7Q1hArkTo2XQkpG_JUU0fdpgiRuoebcZT3BlbkFJTbMHcXre_nSUrX6Jzesp8peW0DYtE8EN0Cnt3zelwA"  # Replace with your actual API key

def get_student_response():
    """Collects student responses for different subjects."""
    subject = input("\nEnter the subject (e.g., History, Science, Mathematics): ").strip()
    
    # Check if the user entered a valid subject. If not, keep asking.
    while subject.lower() not in ['history', 'science', 'mathematics']:
        print("Invalid subject. Please enter a valid subject (History, Science, Mathematics).")
        subject = input("\nEnter the subject (e.g., History, Science, Mathematics): ").strip()
    
    question = input("\nEnter the exam question: ").strip()
    if not question:
        print("Question cannot be empty. Please re-enter.")
        return get_student_response()
    
    print("Enter the student's answer (press Enter twice to finish):")
    user_answer = "\n".join(iter(input, ""))

    if not user_answer.strip():
        print("Student's answer cannot be empty. Please re-enter.")
        return get_student_response()

    marks_options = {"1", "2", "3", "4", "5", "6", "7", "10"}
    marks = input("Enter the marks for the question (1, 2, 3, ..., 7 or 10): ").strip()
    while marks not in marks_options:
        print("Invalid entry. Please enter a valid number from the provided options.")
        marks = input("Enter the marks: ").strip()

    return subject, question, user_answer, int(marks)


def generate_rubric(subject, marks):
    """Dynamically generates the grading rubric based on the subject."""
    rubrics = {
        "History": (
            f"**HISTORY EXAM EVALUATION RUBRIC**\nTotal Marks: {marks} Marks\n"
        ),
        "Science": (
            f"**SCIENCE EXAM EVALUATION RUBRIC**\nTotal Marks: {marks} Marks\n"
        ),
        "Mathematics": (
            f"**MATHEMATICS EXAM EVALUATION RUBRIC**\nTotal Marks: {marks} Marks\n"
        )
    }
    return rubrics.get(subject, "**GENERAL EVALUATION RUBRIC**\nAnswer is graded based on accuracy, clarity, and depth.")

def evaluate_response(subject, question, user_answer, marks):
    try:
        detected_language = "en"
        try:
            detected_language = detect(user_answer)
        except LangDetectException:
            pass
        
        rubric = generate_rubric(subject, marks)
        
        # OpenAI GPT model for evaluation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": rubric},
                {"role": "user", "content": f"{subject} Question: {question}\nStudent Answer: {user_answer}\nTotal Marks: {marks}"}
            ],
            max_tokens=600  # Increase the token limit for more detailed responses
        )

        evaluation_text = response["choices"][0]["message"]["content"].strip()
        print("\n📝 **Evaluation Text from AI:**")
        print(evaluation_text)

        # Extract marks awarded using regex
        marks_match = re.search(r'Marks Awarded[:\-]?\s*(\d*\.?\d+)\s*/\s*(\d+)', evaluation_text)
        awarded_marks = float(marks_match.group(1)) if marks_match else 0

        # Ensure awarded marks do not exceed total marks
        awarded_marks = min(awarded_marks, marks)

        return evaluation_text, awarded_marks, marks
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred during evaluation.", 0, marks

def run_exam_checker():
    """Runs the exam checker for multiple subjects."""
    print("Welcome to the **Multi-Subject Exam Checker**! (Type 'exit' or 'quit' to stop)")

    total_awarded, total_possible = 0, 0
    
    while True:
        try:
            subject, question, user_answer, marks = get_student_response()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting the exam checker...")
            break
        
        evaluation, awarded, total = evaluate_response(subject, question, user_answer, marks)
        
        print(f"\n📜 **{subject} Evaluation Report:**")
        print(evaluation)
        print(f"\n✅ **Marks Awarded:** {awarded}/{total}")
        
        total_awarded += awarded
        total_possible += total

    print("\n🏆 **Final Summary:**")
    print(f"Total Marks Awarded: {total_awarded}")
    print(f"Total Possible Marks: {total_possible}")

# Run the exam checker
run_exam_checker()
