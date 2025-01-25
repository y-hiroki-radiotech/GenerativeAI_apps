# * Agentにどのように動いて欲しいかを指定する
from crewai import Task
from tools import tool
from agents import news_researcher, news_writer

# *Research task
researcher_task = Task(
    description=(
        "Identify the next big tread in {topic}."
        "Focus on identifying pros and cons and the overall narrative."
        "Your final report should clearly articulate the key points,"
        "It's market opportunity, and potential risks."
    ),
    expected_output="A comprehensive 3 paragraphs long report on the latest AI treands.",
    tools=[tool],
    agent=news_researcher,
)

# *Writing task with language model configuration
writer_task = Task(
    description=(
        "Compose an insightful article on {topic}."
        "Focus on the latest trends and how it's impacting the industry."
        "This article should be easy to understanding, engaging, and positive."
    ),
    expected_output="A 4 paragraphs article on {topic} advancements formatted as markdown.",
    tools=[tool],
    agent=news_writer,
    async_execution=False,
    output_file="new-blog-post.md"
)
