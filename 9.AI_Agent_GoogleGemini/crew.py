from crewai import Crew, Process
from agents import news_researcher, news_writer
from tasks import researcher_task, writer_task


# forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[news_researcher, news_writer],
    tasks=[researcher_task, writer_task],
    process=Process.sequential,
)


# starting the task execution process with enhanced feedback
result=crew.kickoff(inputs={'topic':'AI in healthcare. Please in japanese.'})
print(result)
