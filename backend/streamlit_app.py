ionimport streamlit as st
import requests
import json
from typing import List

class ChatHistory:
    def __init__(self):
        self.messages: List[dict] = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def get_all_messages(self) -> List[dict]:
        return self.messages

def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ChatHistory()
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""

def main():
    st.set_page_config(
        page_title="RAG Chatbot",
        page_icon="🤖",
        layout="centered"
    )
    
    initialize_session_state()
    
    # Header
    st.title("🤖 PICT MUN ChatBot")
    st.markdown("""
    You ask any question related to the proceedings.
    """)
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history.get_all_messages():
            if message["role"] == "user":
                st.write(f'👤 **You**: {message["content"]}')
            else:
                st.write(f'🤖 **Bot**: {message["content"]}')
    
    # Input container
    with st.container():
        user_input = st.text_input(
            "Your question:",
            key="user_input",
            placeholder="Type your question here...",
        )
        
        # Send button column
        col1, col2 = st.columns([6, 1])
        with col2:
            send_button = st.button("Send")
        
        if send_button and user_input:
            # Add user message to chat history
            st.session_state.chat_history.add_message("user", user_input)
            
            # Make API call to backend
            try:
                response = requests.post(
                    "http://localhost:8000/generate_response/",
                    json={"query": user_input}
                )
                
                if response.status_code == 200:
                    bot_response = response.json()["response"]
                    # Add bot response to chat history
                    st.session_state.chat_history.add_message("assistant", bot_response)
                else:
                    st.error(f"Error: Failed to get response from server. Status code: {response.status_code}")
                
                # Clear input
                st.session_state.user_input = ""
                
                # Rerun to update the display
                st.experimental_rerun()
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error: Could not connect to the server. Please make sure the backend is running.\n{str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Built by PICT MUN</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
