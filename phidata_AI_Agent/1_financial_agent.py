# https://docs.phidata.com/introduction
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
import os
from dotenv import load_dotenv

load_dotenv()

# https://console.groq.com/docs/models
# *web search agent
websearch_agent = Agent(
    name="Web search Agent",
    role="Search the web for information",
    model=Groq(id="llama3-groq-70b-8192-tool-use-preview"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources. Please in Japanese."],
    show_tools_calls=True,
    markdown=True,
)

# *Financial Agent
finance_agent = Agent(
    name="Finance AI Agent",
    model=Groq(id="llama3-groq-70b-8192-tool-use-preview"),
    tools=[
        YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True,
                      company_news=True)
        ],
    instructions=["Use tables to display the data"],
    show_tools_calls=True,
    markdown=True,
)

multi_ai_agent = Agent(
    team=[websearch_agent, finance_agent],
    instructions=["Always include sources.Please in Japanese.", "Use tables to display the data"],
    show_tools_calls=True,
    markdown=True,
)

multi_ai_agent.print_response("Summarize analyst recommendations and share the latest news for NVIDIA in japanese", stream=True)
