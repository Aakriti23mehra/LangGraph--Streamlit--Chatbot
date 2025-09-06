import streamlit as st
from langraph_database_backend import chatbot, retrieve_all_threads, llm
from langchain_core.messages import HumanMessage
import uuid

### Utility functions
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    
    #  Add default title
    st.session_state['chat_titles'][thread_id] = "New Chat"
    
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

### Session state setup
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

#  each old thread has a title placeholder
for tid in st.session_state['chat_threads']:
    if tid not in st.session_state['chat_titles']:
        st.session_state['chat_titles'][tid] = "Old Chat"

add_thread(st.session_state['thread_id'])

### Sidebar UI
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    title = st.session_state['chat_titles'].get(thread_id, thread_id[:8])
    if st.sidebar.button(title, key=f"btn_{thread_id}"): 
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        # Convert messages into session format
        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})
        st.session_state['message_history'] = temp_messages

### Chat history in main UI
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message['content'])

### Chat input
user_input = st.chat_input('Type here')

if user_input:
    # Save user message
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # If this is the FIRST user message in this chat → generate a title
    if len(st.session_state['message_history']) == 1:  
        title_prompt = f"Summarize this message into 3-5 words for a chat title: {user_input}"
        title = llm.invoke([HumanMessage(content=title_prompt)]).content
        st.session_state['chat_titles'][st.session_state['thread_id']] = title

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Stream assistant response
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # Save assistant message
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})
