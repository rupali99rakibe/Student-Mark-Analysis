import openai
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Set your OpenAI API key
openai.api_key = "your-api-key"

def get_student_input():
    """Function to collect student responses and return question, answer, and marks."""
    question = input("\nEnter the exam question: ")
    if question.lower() in ['exit', 'quit']:
        return None, None, None

    print("Enter the student's answer (press Enter twice to finish):")
    student_answer_lines = []
    while True:
        line = input()
        if line == "":
            break
        student_answer_lines.append(line)
    user_answer = "\n".join(student_answer_lines)
    
    if not user_answer.strip():
        print("Student's answer cannot be empty. Please re-enter.")
        return get_student_input()
    
    while True:
        marks_type = input("Enter the marks for the question (1, 2, 3, ..., 7 or 10): ").strip()
        if marks_type.isdigit() and marks_type in {"1", "2", "3", "4", "5", "6", "7", "10"}:
            return question, user_answer, int(marks_type)
        else:
            print("Invalid marks entry. Please enter a valid number from the options provided.")

def evaluate_response(question, user_answer, marks_type):
    try:
        detected_language = "en"
        try:
            detected_language = detect(question + " " + user_answer)
        except LangDetectException:
            pass

        instructions = (
            f"Evaluate the student's answer based on accuracy, clarity, and relevance. "
            f"Provide a numerical score in the format 'Marks Awarded: X/{marks_type}', ensuring X does not exceed {marks_type}. "
            f"Give concise constructive feedback. Use whole numbers. "
            f"If the student's answer is incorrect or incomplete, suggest a relevant study reference book and chapter. "
            f"Response should be in {detected_language}. Never award full marks for partial answers."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": f"Question: {question}\nStudent Answer: {user_answer}\nTotal Marks: {marks_type}"}
            ],
            max_tokens=400
        )

        if "choices" not in response or not response["choices"]:
            return "Error: No response from OpenAI.", 0, marks_type

        evaluation_text = response["choices"][0]["message"]["content"].strip()

        # Extract marks awarded
        marks_match = re.search(r'Marks Awarded[:\-]?\s*(\d+)\s*/\s*(\d+)', evaluation_text)
        if marks_match:
            awarded_marks = int(marks_match.group(1))
            total_marks = int(marks_match.group(2))
            awarded_marks = min(awarded_marks, marks_type)  # Cap at max marks
        else:
            awarded_marks = 0
            total_marks = marks_type

        return evaluation_text, awarded_marks, total_marks
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't evaluate the response due to an API issue.", 0, marks_type
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred.", 0, marks_type

def run_exam_checker():
    """Main function to run the exam checker loop."""
    print("Welcome to the Exam Checker! (Type 'exit' or 'quit' to stop)")
    total_awarded_marks, total_possible_marks = 0, 0
    
    while True:
        question, user_answer, marks_type = get_student_input()
        if question is None:
            break

        evaluation, awarded_marks, total_marks = evaluate_response(question, user_answer, marks_type)
        print("\nEvaluation:")
        print(evaluation)

        if awarded_marks is not None and total_marks is not None:
            print(f"\nMarks Analysis: {awarded_marks}/{total_marks}")
            total_awarded_marks += awarded_marks
            total_possible_marks += total_marks
        else:
            print("\nEvaluation completed but marks extraction is not available.")

    print("\nExiting Exam Checker. Total Summary:")
    print(f"Total Marks Awarded: {total_awarded_marks}")
    print(f"Total Possible Marks: {total_possible_marks}")

if __name__ == "__main__":
    run_exam_checker()
