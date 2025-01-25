from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# * function to load Gemini Pro model and get response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# * Initialize our streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

# * Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

input = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# * If ask botton is clicked
if submit:
    response = get_gemini_response(input)
    # * Add user query and response to session chat history
    st.session_state["chat_history"].append(("You\n", input))
    st.subheader("The Response is")
    for chunk in response:
        print(st.write(chunk.text))
        st.session_state["chat_history"].append(("Bot\n", chunk.text))

st.subheader("The Chat history is")

for role, text in st.session_state["chat_history"]:
    st.write(f"{role}: {text}")
