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
        instructions="""You are an FAQ assistant for BitGo. Your instructions here.""",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        model="gpt-4-turbo"
    )

# Check if the vector store ID has changed or if an assistant needs to be created
if 'selected_vector_store_id' not in st.session_state or \
        st.session_state.selected_vector_store_id != selected_store_id or \
        'assistant' not in st.session_state:
    st.session_state.assistant = create_assistant(selected_store_id)
    st.session_state.selected_vector_store_id = selected_store_id

assistant = st.session_state.assistant

# Initialization
if 'thread' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread = thread

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
