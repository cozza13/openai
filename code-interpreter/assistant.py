import streamlit as st
from openai import OpenAI
import time

# Define a dictionary mapping vector store names to their IDs
vector_stores = {
    "Q&A Docs": "vs_TI5Xe5OnNrnM0T56iZhsxuI2",
    "API Docs": "vs_zLv5Fyne1KfIaaT3L3zyQO6z",
    # Add more stores as needed
}


# Sidebar UI for selecting a vector store
selected_store_name = st.sidebar.selectbox(
    'Select a Vector Store',
    options=list(vector_stores.keys()),  # Display user-friendly names
)

# Get the ID of the selected vector store
selected_store_id = vector_stores[selected_store_name]

st.sidebar.title('🤖 BitGo FAQ')
avatar = {"assistant": "🤖", "user": "🐱"}

client = OpenAI(
    api_key=st.secrets['OPEN_AI_KEY'],
)

# Function to create a new assistant
def create_assistant(vector_store_id):
    return client.beta.assistants.create(
        name="BitGo FAQ Assistant",
        instructions="""You are an FAQ assistant for BitGo. For every question you receive, follow these steps:\n\nStep 1: Analyze the question to determine the user's intent and the type of information they are seeking, such as API information, system navigation, or general information.\n\nStep 2: Perform a thorough search of the attached files using the file_search function, focusing on the areas identified in Step 1. If the question involves API requests, ensure that you have the complete and accurate path before searching.\n\nStep 3: If the file_search yields relevant information, use it to construct a clear, structured response that directly addresses the user's question. Format your response appropriately, such as using code blocks for API examples or bullet points for step-by-step instructions.\n\nStep 4: If, after searching the attached files, you do not have sufficient information to answer the question confidently, simply respond with, "I apologize, but I do not have enough information in the provided files to answer your question accurately." Do not attempt to generate an answer or provide information that is not directly sourced from the attached files.\n\nRemember, your primary goal is to provide accurate, helpful information to the user based solely on the content of the attached files. Do not introduce any information or speculation that cannot be directly attributed to the search results. If you are unsure or the information is not available, it is better to acknowledge this limitation than to provide a potentially incorrect or misleading response.""",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        model="gpt-4-turbo"
    )

# Function to create a new thread
def create_new_thread():
    return client.beta.threads.create()

# Check if the vector store ID has changed
if 'selected_vector_store_id' not in st.session_state or \
        st.session_state.selected_vector_store_id != selected_store_id:
    
    # Create a new assistant and update the session state
    st.session_state.assistant = create_assistant(selected_store_id)
    st.session_state.selected_vector_store_id = selected_store_id
    
    # Create a new thread and update the session state
    st.session_state.thread = create_new_thread()

# Use the assistant and thread from the session state
assistant = st.session_state.assistant
thread = st.session_state.thread

st.sidebar.write('## What to do')
st.sidebar.write("Ask me questions about BitGo FAQ documents?")

if prompt := st.chat_input():
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
    )

    run_status = "pending"
    while run_status != "completed":
        time.sleep(5)  # Wait for 5 seconds before checking the status again
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        run_status = run.status  # Update run_status with the current status

    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )

    for line in messages.data[::-1]:
        st.chat_message(line.role, avatar=avatar[line.role]).write(line.content[0].text.value)
