from dotenv import load_dotenv
import streamlit as st
import os
# import google.generativeai as genai
from google import genai

load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# *function to load Gemini Pro Model and get response
# model = genai.GenerativeModel("gemini-pro")
def get_gemini_response(question):
    # response = model.generate_content(question)
    response = client.models.generate_content(
        model="gemini-pro", contents=question
    )
    return response.text

# *Initialize our streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

input = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

#* When submit is clicked
if submit:
    response = get_gemini_response(input)
    st.subheader("The Response is")
    st.write(response)
