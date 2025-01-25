from config import *
from models import State
from nodes import selection_node, answering_node, check_node
from langgraph.graph import StateGraph, END
import streamlit as st

# グラフの作成
workflow = StateGraph(State)

workflow.add_node("selection", selection_node)
workflow.add_node("answering", answering_node)
workflow.add_node("check", check_node)

# エッジの定義
workflow.set_entry_point("selection")
workflow.add_edge("selection", "answering")
workflow.add_edge("answering", "check")

# 条件付きエッジの定義
workflow.add_conditional_edges(
    "check",
    lambda state: state.current_judge,
    {True: END, False: "selection"}
)

compiled = workflow.compile()

def main():
    st.set_page_config(page_title="Langchain WorkFlow")
    st.header("Q＆Aエキスパート")

    input = st.text_input("質問を入力してください:", key="input")
    submit = st.button("回答")
    if submit:
        with st.spinner("回答を生成中・・・"):
            initial_state = State(query=input)
            result = compiled.invoke(initial_state)
            st.write(result["messages"][-1])

if __name__ == "__main__":
    main()
