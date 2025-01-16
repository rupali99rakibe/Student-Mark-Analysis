import openai

# Set your OpenAI API key
openai.api_key = "OPENAI_API_KEY"

def generate_response(user_input):
    try:
        # Make the API call to get the AI response
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use a robust model (e.g., "gpt-4")
            messages=[
                {"role": "system", "content": (
                    "You are a knowledgeable and friendly assistant. "
                    "Provide accurate, concise, and subject-appropriate responses. "
                    "For equations or formulas, provide them in plain text. For historical or literary queries, offer clear and concise summaries. "
                    "For all queries, adapt to the subject matter while ensuring clarity and correctness."
                )},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200  # Adjust token limit to allow detailed responses
        )
        
        # Extract and return the response content
        return response["choices"][0]["message"]["content"].strip()
    
    except openai.OpenAIError as e:
        print(f"An error occurred: {e}")
        return "Sorry, I couldn't process your request."

if __name__ == "__main__":
    print("Welcome to the Generative AI Model! Ask me about any subject! (Type 'exit' or 'quit' to stop)")
    
    while True:
        user_input = input("You: ")
        
        # Exit condition
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting the Generative AI Model. Goodbye!")
            break
        
        ai_response = generate_response(user_input)
        print(f"AI: {ai_response}")
