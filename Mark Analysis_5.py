import json
import pymongo
import openai

# Database Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ExamDatabase"]
questions_collection = db["questions"]
answers_collection = db["answers"]

# OpenAI API Key (Use Environment Variable in Production)
openai.api_key = "your-api-key"

def getQuestionDetails(QuestionID):
    question = questions_collection.find_one({"QuestionID": QuestionID})
    if question:
        return {
            "question": question.get('question'),
            "evaluation_criteria": question.get('evaluation_criteria'),
            "ideal_answer": question.get('ideal_answer'),
            "marks": question.get('marks')
        }
    return {"error": "Question not found!"}

def getStudentAnswer(QuestionID, StudentID):
    student_answer = answers_collection.find_one({
        "QuestionID": QuestionID,
        "StudentID": StudentID
    })
    if student_answer:
        return {
            "QuestionID": student_answer['QuestionID'],
            "StudentID": student_answer['StudentID'],
            "Student_answer": student_answer['Student_answer']
        }
    return {"error": "Student answer not found!"}

def GenerateSystemPrompt(question_details):
    prompt = f"""
    You are an AI evaluator assessing a student's answer. Evaluate the response based on the given criteria and strictly follow these instructions:
    
    1. Compare the student's answer with the ideal answer.
    2. Assess the response based on the given evaluation criteria.
    3. Assign marks out of {question_details['marks']} based on correctness and completeness.
    4. Provide a clear reason for the marks given.
    5. If necessary, suggest improvements based on the ideal answer.
    
    Format your response strictly as JSON:
    {{
        "marks": <numeric_value>,
        "reason": "<justification>",
        "reference": "<if any, otherwise null>"
    }}
    
    Here is the question and the details:

    Question: {question_details['question']}
    Evaluation Criteria: {question_details['evaluation_criteria']}
    Ideal Answer: {question_details['ideal_answer']}
    Marks Available: {question_details['marks']}
    
    Student's answer will be provided next.
    """
    return prompt

def validate_marks(assigned_marks, total_marks):
    if not isinstance(assigned_marks, (int, float)) or assigned_marks < 0 or assigned_marks > total_marks:
        return False
    return True

def evaluateStudentAnswer(prompt, student_answer):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": student_answer}
        ],
        max_tokens=300
    )
    
    try:
        evaluation = json.loads(response['choices'][0]['message']['content'])
        if not validate_marks(evaluation.get("marks"), 10):  # Example total marks: 10
            return {"error": "Invalid marks assigned by AI"}
    except (json.JSONDecodeError, ValueError) as e:
        return {"error": "AI response could not be processed", "details": str(e)}

    return evaluation

# Example Usage
QuestionID = "Q123"
StudentID = "S456"

question_details = getQuestionDetails(QuestionID)
if "error" in question_details:
    print(question_details)
else:
    student_answer_data = getStudentAnswer(QuestionID, StudentID)
    if "error" in student_answer_data:
        print(student_answer_data)
    else:
        system_prompt = GenerateSystemPrompt(question_details)
        result = evaluateStudentAnswer(system_prompt, student_answer_data["Student_answer"])
        print(result)
