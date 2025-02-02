import openai
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import time

# Set your OpenAI API key
openai.api_key = "sk-jxHNeitHqQ7Q1hArkTo2XQkpG_JUU0fdpgiRuoebcZT3BlbkFJTbMHcXre_nSUrX6Jzesp8peW0DYtE8EN0Cnt3zelwA"  # Replace with your actual OpenAI API key

def collect_student_response():
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
    
    while True:
        marks = input("Enter the marks for the question (1, 2, 3, ..., 7 or 10): ").strip()
        if marks.isdigit() and marks in {"1", "2", "3", "4", "5", "6", "7", "10"}:
            return question, user_answer, int(marks)
        else:
            print("Invalid marks entry. Please enter a valid number from the options provided.")

def safe_api_call(model, messages, max_tokens=400, retries=3):
    """Handles OpenAI API call errors and retries if needed."""
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return response
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error: {e}. Retrying ({attempt+1}/{retries})...")
            time.sleep(2)
    return None

def evaluate_response(question, user_answer, marks):
    """Evaluates a student's response using OpenAI GPT-4 with strict grading rules."""
    try:
        if not user_answer.strip():
            return f"**Marks Awarded: 0/{marks}**\n**Feedback:** Unanswered the question.\n**Study Reference:** Read your textbook or class notes on this topic.", 0, marks

        detected_language = "en"
        try:
            detected_language = detect(user_answer)  
        except LangDetectException:
            pass

        prompt = f"""
You are an AI exam evaluator. Your task is to **strictly** assess a student's answer based on accuracy, clarity, and relevance.

### **Evaluation Guidelines:**
1. **Full Marks:** Awarded only if the answer is **complete, correct, and well-articulated**.
2. **Partial Marks:** Deduct marks for **missing information, incorrect details, or lack of clarity**.
3. **Zero Marks:** If the answer is **completely incorrect, irrelevant, or missing key concepts**.
4. **No Assumptions:** Only evaluate based on the exact words provided in the student's response.
5. **Concise Feedback:** Limit feedback to key strengths and areas for improvement.

---
### **Strict Response Format:**
- **Marks Awarded: X/{marks}** (Ensure `X` does not exceed `{marks}`)
- **Feedback:** [A brief evaluation focusing on correctness, clarity, and relevance]
- **Study Reference:** [If the answer is incomplete or incorrect, suggest a book, article, or website to improve understanding.]

---
### **Now, evaluate the following student response strictly according to these rules:**
Question: {question}  
Student Answer: {user_answer}  
Total Marks: {marks}

Return your response **ONLY in the format specified above**.
"""

        response = safe_api_call(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI exam evaluator, strictly following structured assessment rules."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        if not response or "choices" not in response or not response["choices"]:
            return "Error: No response from OpenAI.", 0, marks

        evaluation_text = response["choices"][0]["message"]["content"].strip()

        marks_match = re.search(r'Marks Awarded[:\-]?\s*(\d*\.?\d+)\s*/\s*(\d+)', evaluation_text)
        if marks_match:
            awarded_marks = float(marks_match.group(1))
            total_marks = int(marks_match.group(2))
            awarded_marks = min(awarded_marks, marks)  
        else:
            awarded_marks = 0  
            total_marks = marks

        return evaluation_text, awarded_marks, total_marks
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred.", 0, marks

def run_exam_checker():
    """Main function to run the exam checker loop."""
    print("Welcome to the Exam Checker! (Type 'exit' or 'quit' to stop)")
    total_awarded_marks, total_possible_marks = 0, 0
    
    while True:
        question, user_answer, marks = collect_student_response()
        if question is None:
            break

        evaluation, awarded_marks, total_marks = evaluate_response(question, user_answer, marks)
        print("\nEvaluation:")
        print(evaluation)

        print(f"\nMarks Analysis: {awarded_marks}/{total_marks}")
        total_awarded_marks += awarded_marks
        total_possible_marks += total_marks
    
    print("\nExiting Exam Checker. Total Summary:")
    print(f"Total Marks Awarded: {total_awarded_marks}")
    print(f"Total Possible Marks: {total_possible_marks}")

# Run the exam checker
run_exam_checker()
