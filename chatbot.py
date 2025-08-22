import pandas as pd
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_response(messages, model="gpt-4o", max_length=300):
    """Generate a response using the chat completions API"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_length
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def get_employee_context(employee_id):
    df = pd.read_csv('assets/data/employee_data.csv')
    employee = df[df['EmployeeID'] == employee_id].iloc[0]
    print(employee)
    print(f"Employee: {employee['Age']} years old, {employee['Tenure']} years tenure, {employee['Department']} department, {employee['Gender']}")
    return f"Employee: {employee['Age']} years old, {employee['Tenure']} years tenure, {employee['Department']} department, {employee['Gender']}"

employee_id_str = input("What is your employee ID?")
employee_id = int(employee_id_str)
employee_context = get_employee_context(employee_id)

messages = [{"role": "system", "content": ""}]

user_input = input("What policy can I help you with today? To finish this conversation please write 'quit'.")
while user_input != "quit":
    
    POLICIES = "Use conversation history to provide helpful guidance."
        
    messages[0]["content"] = f"""You are TechLance's AI assistant specializing in employee policies.

         ROLE: Translate complex policies into clear, actionable advice
         STYLE: Professional yet conversational, concise but complete
         PERSONALIZATION: Tailor all responses to this employee profile: {employee_context}

         GUIDELINES:
         - Use simple language, avoid jargon
         - Give specific numbers, dates, and examples
         - Focus on what matters most to THIS employee
         - Keep responses under 150 words unless complex calculations needed
         - Always explain "why this matters to you"
         
         Use this policy info: {POLICIES}"""
    
    messages.append({"role": "user", "content": user_input})
    
    assistant_response = get_response(messages)
    print(f"Assistant: {assistant_response}")
    messages.append({"role": "assistant", "content": assistant_response})
    user_input = input("")