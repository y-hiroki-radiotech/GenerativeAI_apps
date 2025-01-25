from crewai import Agent, LLM
import os
from dotenv import load_dotenv

from tools import tool

load_dotenv()

# * Call the gemini models
llm=LLM(model="gemini/gemini-1.5-flash",
        verbose=True,
        api_key=os.getenv("GOOGLE_API_KEY"))

# * Creating a senior researcher agent with memory and verbose mode
news_researcher = Agent(
    role="Senior Researcher",
    goal="Uncover ground breaking technologies in {topic}",
    verbose=True,
    memoryview=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of"
        "innovation, eager to explore and share knowledge that could change"
        "the world."
    ),
    tools=[tool],
    allow_delegation=True,
    llm=llm  # LLMプロバイダーを指定
)

# *Creating a write agent with custom tools responsible in writing news blog
news_writer = Agent(
    role="Writer",
    goal="Narrate compelling tech stories about {topic}",
    verbose=True,
    memoryview=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft"
        "engaging narratives that captivate and educate, bringing new"
        "discoveries to light in an accessible manner."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)
