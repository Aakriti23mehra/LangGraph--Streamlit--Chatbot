import streamlit as st
from backend_langgraph import chatbot
from langchain_core.messages import  HumanMessage
import uuid    #In Python, a UUID (Universally Unique IDentifier) is a 128-bit number used to uniquely identify information in computer systems.
### utility functions
#this will always generate a random thread id
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config= {'configuarable':{'thread_id':thread_id}}).values['messages']
#initializes the persistent history  ,session setup ,page load

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = [] 

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])
 
# Side bar UI
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations ")


for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str('thread_id')):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        #code to make it compatible according to the message history 
        temp_messages = []
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role = 'user'
            else :
                role = 'assistant'
            temp_messages.append({'role':role,'content':msg.content})
        st.session_state['message_history'] = temp_messages


#loading ht coservation history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message['content'])

user_input = st.chat_input('Type here')

#add the user message to the history and diplsy it in ui


if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable':{'thread_id': st.session_state['thread_id']}}
    
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk ,metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]}, 
                config= CONFIG,
                stream_mode= 'messages'
            )

            )
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})


    #our message history is the list of dictionaries ,each dict has tow keys and values
    #[{'role' :'user' ,'content' :'hi'}
    #{'role' : 'assistant' ,'content' :'hello'}]