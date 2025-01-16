import openai

# Set your OpenAI API key
openai.api_key = "OPENAI_API_KEY"

def evaluate_response(question, user_answer, marks_type):
    try:
        # Map input marks to appropriate instructions
        marks_mapping = {
            "1": "1-2",
            "2": "1-2",
            "3": "3-4",
            "4": "4-5",
            "5": "5-7",
            "6": "5-7",
            "7": "5-7"
        }

        # Normalize the marks type
        normalized_marks_type = marks_mapping.get(marks_type, marks_type)

        # Define evaluation instructions based on normalized marks type
        if normalized_marks_type == "1-2":
            instructions = (
                "You are an evaluator for short-answer questions worth 1-2 marks. Evaluate the answer based on relevance and accuracy. "
                "Award full marks for correct and concise answers. Penalize for errors or lack of clarity."
            )
        elif normalized_marks_type == "3-4":
            instructions = (
                "You are an evaluator for medium-length questions worth 3-4 marks. Evaluate the answer based on relevance, structure, and level of detail. "
                "Award marks for providing a clear and reasonably detailed explanation. Penalize for missing key points or lack of clarity."
            )
        elif normalized_marks_type == "4-5":
            instructions = (
                "You are an evaluator for detailed questions worth 4-5 marks. Evaluate the answer based on depth, clarity, and explanation. "
                "Award marks for including important details and structured explanations. Penalize for insufficient or vague content."
            )
        elif normalized_marks_type == "5-7":
            instructions = (
                "You are an evaluator for long-answer questions worth 5-7 marks. Evaluate the answer based on depth, clarity, explanation, and use of diagrams. "
                "Award marks for detailed explanations and accurate diagrams. Penalize for missing key elements or unclear diagrams."
            )
        else:
            return "Invalid marks type. Please choose from 1-2, 3-4, 4-5, or 5-7.", None

        # Make API call to GPT-4 for evaluation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": (
                    f"Question: {question}\n\n"
                    f"Student Answer: {user_answer}\n\n"
                    f"Total Marks: {marks_type}\n"
                    f"Provide awarded marks and feedback."
                )}
            ],
            max_tokens=500  # Allow detailed feedback
        )

        # Extract and return the evaluation and feedback
        evaluation_text = response["choices"][0]["message"]["content"].strip()

        # Extract marks awarded (assuming GPT outputs something like 'Marks awarded: X/Y')
        import re
        marks_match = re.search(r'Marks\s*awarded\s*:\s*(\d+)\s*/\s*(\d+)', evaluation_text, re.IGNORECASE)
        if marks_match:
            awarded_marks = int(marks_match.group(1))
            total_marks = int(marks_match.group(2))
        else:
            # Fallback if marks cannot be parsed
            awarded_marks = None
            total_marks = None

        return evaluation_text, awarded_marks, total_marks

    except openai.OpenAIError as e:
        print(f"An error occurred: {e}")
        return "Sorry, I couldn't evaluate the response.", None, None

if __name__ == "__main__":
    print("Welcome to the Exam Checker! Evaluate student responses easily. (Type 'exit' or 'quit' to stop)")

    while True:
        # Input the exam question
        question = input("\nEnter the exam question: ")

        # Exit condition
        if question.lower() in ['exit', 'quit']:
            print("Exiting the Exam Checker. Goodbye!")
            break

        # Input student's answer
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
            continue

        # Input the marks type
        marks_type = input("Enter the marks for the question (1, 2, 3, ..., 7 or ranges like 1-2, 3-4): ").strip()

        # Evaluate the student's answer
        evaluation, awarded_marks, total_marks = evaluate_response(question, user_answer, marks_type)

        # Print the evaluation feedback
        print("\nEvaluation:")
        print(evaluation)

        # Print the marks breakdown if available
        if awarded_marks is not None and total_marks is not None:
            print(f"\nMarks Analysis: {awarded_marks}/{total_marks}")
        else:
            print("\nMarks Analysis: Unable to extract marks.")
