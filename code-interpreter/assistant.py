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
        instructions="You are an FAQ assistant for BitGo, always look at the attached files for all questions you are asked.  If you are looking at API requests make sure you have the full correct path. If you do not know the answer just say 'I do not know the answer'. When you are answering the questions do the following.  Step 1. Think through the meaning of the question and break out if the person is wanting to know about API information, navigating the system, general information. The do the search with file_search. Step 2. Based on what you have from Step 1 you should answer the question by running a file_search function addressing each area they are interested in output them in a structured format. ",
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

    time.sleep(20)

    run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
    )
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )
    # st.write(messages.data[::-1])
    for line in messages.data[::-1]:
        st.chat_message(line.role,avatar=avatar[line.role]).write(line.content[0].text.value)
      

