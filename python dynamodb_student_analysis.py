import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('GradesTable')

# Define StudentID
student_id = 'student123'

# Query DynamoDB using GSI on StudentID (Ensure GSI is created for efficient querying)
response = table.query(
    IndexName='StudentID-Index',  # Ensure you have a GSI on StudentID
    KeyConditionExpression='StudentID = :s_id',
    ExpressionAttributeValues={':s_id': student_id}
)

# Initialize variables
total_assigned_marks = Decimal(0)
total_possible_marks = Decimal(0)
total_questions = 0
scorecard = []

# Function to generate feedback based on performance
def generate_feedback(score):
    if score >= 90:
        return "Excellent performance"
    elif score >= 75:
        return "Good job, but there's room for improvement"
    elif score >= 60:
        return "Fair performance, consider revising key concepts"
    else:
        return "Needs improvement, focus on weak areas"

# Process the retrieved data
for item in response['Items']:
    assigned_marks = Decimal(item['assigned_marks'])
    total_marks = Decimal(item['total_marks'])
    percentage_score = (assigned_marks / total_marks) * 100 if total_marks > 0 else 0
    feedback = generate_feedback(percentage_score)

    scorecard.append({
        "QuestionID": item['QuestionID'],
        "Question Details": item['question_details'],
        "Assigned Marks": assigned_marks,
        "Total Marks": total_marks,
        "Score Percentage": round(percentage_score, 2),
        "Grade": item['Grade'],
        "Feedback": feedback
    })

    total_assigned_marks += assigned_marks
    total_possible_marks += total_marks
    total_questions += 1

# Calculate overall performance
overall_percentage = (total_assigned_marks / total_possible_marks) * 100 if total_possible_marks > 0 else 0
average_score = overall_percentage / total_questions if total_questions > 0 else 0
overall_feedback = generate_feedback(overall_percentage)

# Print Student's Scorecard
print(f"\nScorecard for Student ID: {student_id}")
print("=" * 50)
for record in scorecard:
    print(f"QuestionID: {record['QuestionID']}")
    print(f"Question Details: {record['Question Details']}")
    print(f"Assigned Marks: {record['Assigned Marks']} / {record['Total Marks']}")
    print(f"Score Percentage: {record['Score Percentage']}%")
    print(f"Grade: {record['Grade']}")
    print(f"Feedback: {record['Feedback']}")
    print("-" * 50)

# Print Overall Performance Analysis
print("\nPerformance Analysis")
print("=" * 50)
print(f"Overall Percentage: {round(overall_percentage, 2)}%")
print(f"Average Score per Question: {round(average_score, 2)}%")
print(f"Overall Feedback: {overall_feedback}")

# Additional Queries:
# Get all grades for a specific QuestionID
def get_grades_for_question(question_id):
    response = table.query(
        KeyConditionExpression="QuestionID = :q_id",
        ExpressionAttributeValues={":q_id": question_id}
    )
    return response['Items']

# Filter student performance by assigned_marks range
def filter_by_marks_range(min_marks, max_marks):
    response = table.scan(
        FilterExpression="assigned_marks BETWEEN :min_marks AND :max_marks",
        ExpressionAttributeValues={":min_marks": min_marks, ":max_marks": max_marks}
    )
    return response['Items']
