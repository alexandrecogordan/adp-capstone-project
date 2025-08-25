import streamlit as st
import pandas as pd
from openai import OpenAI
import os 
import json

#/home/ec2-user/SageMaker/adp-capstone-project
#do NOT forget to do export OPENAI_API_KEY='' in terminal first

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_response(messages, model="gpt-4o", max_length=300):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_length
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

def get_employee_context(employee_id):
    try:
        df = pd.read_csv('assets/data/employee_data.csv')
        employee = df[df['EmployeeID'] == employee_id].iloc[0]
        return f"Employee: {employee['Age']} years old, {employee['Tenure']} years tenure, {employee['Department']} department, {employee['Gender']}"
    except Exception as e:
        st.error(f"Error loading employee data: {e}")
        return None

st.set_page_config(page_title="TechLance AI Assistant", page_icon="🤖")
st.title("TechLance AI Assistant")
st.subheader("Want to learn more about TechLance's policies? You are at the right place!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "employee_context" not in st.session_state:
    st.session_state.employee_context = None

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# Allow user to change the employee number 
if st.session_state.employee_context:
    if st.button("Change Employee"):
        st.session_state.employee_context = None
        st.session_state.messages = []
        st.rerun()
        
if st.session_state.employee_context:
    welcome_message = "What policy would you like to learn more about?"
else:
    welcome_message = "Please enter employee ID."

if st.session_state.employee_context:
    with st.sidebar:
        st.header("👤 Employee Info")
        
        context = st.session_state.employee_context
        parts = context.replace("Employee: ", "").split(", ")
        
        st.write(f"**Age:** {parts[0].replace(' years old', '')}")
        st.write(f"**Tenure:** {parts[1].replace(' years tenure', '')}")
        st.write(f"**Department:** {parts[2].replace(' department', '')}")
        st.write(f"**Gender:** {parts[3]}")

if prompt := st.chat_input(welcome_message):
    # Add user message to conversation history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user's message in the chat interface
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if input is a number (employee ID) or text (policy question)
    try:
        # Try to convert input to integer: if successful, it's an employee ID
        employee_id = int(prompt)
        # Load employee data from CSV using the ID
        st.session_state.employee_context = get_employee_context(employee_id) # This creates the employee context
        # Create confirmation response with employee details
        response = f"What policy can I help with?" # Loaded: {st.session_state.employee_context}. 

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() # changes the welcome message so reruns everything but still keeps employee context
    except ValueError:
        # Input is not a number, so it's a policy question
        if st.session_state.employee_context:
            # Employee context exists, so process the policy question
            # Open and read the policies JSON file
            with open('policies.json', 'r') as f:
                policies_data = json.load(f)
            # Convert policies dictionary to formatted string
            POLICIES = "\n".join([f"{k}: {v}" for k, v in policies_data.items()])
            
            # Create system message with employee context and policies
            system_msg = {"role": "system", "content": f"""You are TechLance's AI assistant specializing in employee policies.

         ROLE: Translate complex policies into clear, actionable advice
         STYLE: Professional yet conversational, concise but complete and helpful tone
         PERSONALIZATION: Tailor all responses to this employee profile: {employee_context}

         GUIDELINES:
         - Use simple language, avoid jargon
         - Give specific numbers, dates, and examples
         - Focus on what matters most to THIS employee
         - Keep responses under 150 words unless complex calculations needed
         - Always explain "why this matters to you"
         - If policy doesn't apply to this employee, explain why
                  
         Use policies: {POLICIES}"""}
            # Combine system message with conversation history
            api_messages = [system_msg] + st.session_state.messages
            
            # Send to OpenAI API and get response
            response = get_response(api_messages)
        else:
            # No employee context loaded yet, ask for employee ID first
            response = "Please enter your employee ID first."
    
    # Display the assistant's response in the chat interface
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})