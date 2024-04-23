import streamlit as st
from openai import OpenAI
import time

st.sidebar.title('🤖 BitGo FAQ')
avatar = {"assistant": "🤖", "user": "🐱"}
client = OpenAI(
    api_key=st.secrets['OPEN_AI_KEY'],
)
@st.cache_resource
def create_assistant():
    return client.beta.assistants.create(
        name="Math Tutor",
        instructions="""You are an FAQ assistant for BitGo. For every question you receive, follow these steps:\n\nStep 1: Analyze the question to determine the user's intent and the type of information they are seeking, such as API information, system navigation, or general information.\n\nStep 2: Perform a thorough search of the attached files using the file_search function, focusing on the areas identified in Step 1. If the question involves API requests, ensure that you have the complete and accurate path before searching.\n\nStep 3: If the file_search yields relevant information, use it to construct a clear, structured response that directly addresses the user's question. Format your response appropriately, such as using code blocks for API examples or bullet points for step-by-step instructions.\n\nStep 4: If, after searching the attached files, you do not have sufficient information to answer the question confidently, simply respond with, "I apologize, but I do not have enough information in the provided files to answer your question accurately." Do not attempt to generate an answer or provide information that is not directly sourced from the attached files.\n\nRemember, your primary goal is to provide accurate, helpful information to the user based solely on the content of the attached files. Do not introduce any information or speculation that cannot be directly attributed to the search results. If you are unsure or the information is not available, it is better to acknowledge this limitation than to provide a potentially incorrect or misleading response.""",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": ["vs_TI5Xe5OnNrnM0T56iZhsxuI2"]}},
        model="gpt-4-turbo"
    )

assistant = create_assistant()

#st.sidebar.write('## Assistant ID')
#st.sidebar.write(assistant.id)

# Initialization
if 'thread' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread = thread

thread = st.session_state.thread
#st.sidebar.write('## Thread ID')
#st.sidebar.write(thread.id)

# if st.sidebar.button('Delete Thread'):
#     client.beta.threads.delete(thread.id)

st.sidebar.write('## What to do')
st.sidebar.write("Ask me questions about BitGo FAQ documents?")

if prompt := st.chat_input():

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    # thread_messages = client.beta.threads.messages.list(thread_id=thread.id)
    # st.sidebar.write(thread_messages.data)

    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
    # instructions="Please address the user as Jane Doe. The user has a premium account."
    )

    run_status = "pending"
    while run_status != "completed":
        time.sleep(5)  # Wait for 5 seconds before checking the status again
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        #st.write(run)
        run_status = run.status  # Update run_status with the current status
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )
    # st.write(messages.data[::-1])
    for line in messages.data[::-1]:
        st.chat_message(line.role,avatar=avatar[line.role]).write(line.content[0].text.value)
      

