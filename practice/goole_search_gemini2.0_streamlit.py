import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# Google検索を利用
google_search_tool = types.Tool(google_search = types.GoogleSearch())

# コンテンツの生成
def get_gemini_response(question):
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=question,
        config=types.GenerateContentConfig(
            tools=[google_search_tool]
        )
    )
    return response

user_prompt = st.text_area("質問内容", "2025年の箱根駅伝で優勝したチームはどこ？")

generate_button = st.button("生成")
if generate_button:
    response = get_gemini_response(user_prompt)
    st.write(response.text)
