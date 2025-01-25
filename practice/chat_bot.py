from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai

load_dotenv()
# Geminiからのresponseを取得
def config_options():
    st.sidebar.selectbox("モデルを選択してください:", (
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-thinking-exp"
    ), key="model_name")

    # checkboxにデフォルトでチェックが入っている状態。このチェックの情報がuse_chat_historyに入る
    st.sidebar.checkbox("チャット履歴を利用しますか?", key="use_chat_history", value=True)
    st.sidebar.button("再開始", key="clear_conversation")
    st.sidebar.expander("セッション状態").write(st.session_state)

# メッセージを初期化
def init_messages():
    if st.session_state.clear_conversation or "messages" not in st.session_state:
        st.session_state.messages = []

# chat履歴を取得
def get_chat_history():
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - 7)
    for i in range(start_index, len(st.session_state.messages) - 1):
        chat_history.append(st.session_state.messages[i])
    return chat_history

# プロンプトを作成
def create_prompt(myquestion):
    # チェックボックスにチェックが入っている場合
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
    else:
        chat_history = ""

    prompt = f"""
    <chat_history>タグと</chat_history>タグの間にあるチャット履歴に含まれる情報を考慮したチャットを提供してください。
    <question>タグと</question>タグの間に含まれる質問に簡潔に答えてください。
    情報を持っていない場合は、そのように言ってください。
    回答に使用した文脈には触れないでください。
    回答に使用したチャット履歴には触れないでください。

    <chat_history>
    {chat_history}
    </chat_history>
    <question>
    {myquestion}
    </question>
    回答:
    """
    return prompt

# 質問に対する応答を生成
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(myquestion):
    model = genai.GenerativeModel(st.session_state.model_name)
    prompt = create_prompt(myquestion)
    response = model.generate_content(prompt)
    return response.text

# Streamlitアプリのタイトル
st.title(":speech_balloon: Gemini チャットボット")

# 設定オブションを表示
config_options()
# メッセージを初期化
init_messages()

# 再実行時に履歴からチャットメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# アプリケーション使用者の入力を受け付ける
question = st.chat_input("テキストを入力してください")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        question = question.replace("'", "")

        with st.spinner(f"{st.session_state.model_name}考え中..."):
            response = get_gemini_response(question)
            message_placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
