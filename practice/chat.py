from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from streamlit_extras.bottom_container import bottom

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# *function to load Gemini Pro model and get response
model = genai.GenerativeModel("gemini-pro")
# !チャットモデルの場合は、チャットの会話履歴を保持するためのhistoryを用いる
chat = model.start_chat(history=[])

def get_gemini_response(question):
    # chat.send_messageを使う
    # ToDo: stream=TrueとFalseを比較する
    response = chat.send_message(question)
    return response

# *Initiaiize our streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

# *Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

with bottom():
    input = st.text_input("Input: ", key="input")
    submit = st.button("Ask the question")

if len(st.session_state["chat_history"]) > 0:
    st.subheader("The Chat history is")

    for role, text in st.session_state["chat_history"]:
        st.write(f"{role}: {text}")

# *If ask button is clicked
if submit:
    st.write("You: ", input)
    response = get_gemini_response(input)
    # *Add user query and response to session chat history
    st.session_state["chat_history"].append(("You\n", input))
    st.subheader("The Response is")
    for chunk in response:
        print(st.write(chunk.text))
        st.session_state["chat_history"].append(("Assistant\n", chunk.text))



