import argparse
from langchain_openai import ChatOpenAI
from agents import DocumentationAgent
from logger import logger


def main():
    parser = argparse.ArgumentParser(description="ユーザー要求に基づいて要件定義を生成します")
    parser.add_argument("--task", type=str, help="生成したいアプリケーションについて記載してください")
    parser.add_argument("--k", type=int, default=5, help="生成するペルソナの人数を設定してください（デフォルト:5}")
    args = parser.parse_args()

    logger.info("Initializing ChatOpenAI model")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    agent = DocumentationAgent(llm=llm, k=args.k)
    logger.info("Running DocumentationAgent")
    final_output = agent.run(user_request=args.task)
    logger.info("Finished running DocumentationAgent")

    print(final_output)


if __name__ == "__main__":
    main()
