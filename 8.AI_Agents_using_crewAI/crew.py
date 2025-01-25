from crewai import Crew, Process
from agents import blog_researcher, blog_writer
from tasks import research_task, write_task

from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceHub
from crewai_tools import SerperDevTool


load_dotenv()

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llm = HuggingFaceHub(
    repo_id=repo_id, model_kwargs={"temperature": 0.5, "max_tokens": 4096}
)
search_tool = SerperDevTool()

# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[blog_researcher, blog_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    memoryview=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)


# Starting the task execution process with enhanced feedback
result = crew.kickoff(inputs={'topic': 'AI vs ML VS DL VS Data Science'})
print(result)
