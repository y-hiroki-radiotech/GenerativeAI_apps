from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# from suprise_trip.tools.custom_tool import MyCustomTool

from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field
from typing import List, Optional


class Activity(BaseModel):
    name: str = Field(..., description="Name of the activity")
    location: str = Field(..., description="Location of the activity")
    description: str = Field(..., description="Description of the activity")
    date: str = Field(..., description="Date of the activity")
    cousine: str = Field(..., description="Cousine of the restaurant")
    why_its_suitable: str = Field(..., description="Why it's suitable for the traveler")
    reviews: Optional[List[str]] = Field(..., description="List of reviews")
    rating: Optional[float] = Field(..., description="Rating of the activity")

class DayPlan(BaseModel):
    date: str = Field(..., description="Date of the day")
    activities: List[Activity] = Field(..., description="List of activities")
    restaurants: List[str] = Field(..., description="List of restaurants")
    flight: Optional[str] = Field(None, description="Flight information")

class Itinerary(BaseModel):
    name: str = Field(..., description="Name of the itinerary, somthing funny")
    day_plans: List[DayPlan] = Field(..., description="List of day plans")
    hotel: str = Field(..., description="Hotel information")


@CrewBase
class SurpriseTravelCrew:
    """SupriseTravel Crew"""
    agent_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def personalized_activity_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['personalized_activity_planner'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def restaurants_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["restaurants_scout"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["itinerary_planner"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
            allow_delegation=False,
        )

    @task
    def personalized_activity_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["personalized_activity_planning_task"],
            agent=self.personalized_activity_planner(),
        )

    @task
    def restaurant_scenic_location_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config["restaurant_scenic_location_scout_task"],
            agent=self.restaurants_scout(),
        )

    @task
    def itinerary_compilation_task(self) -> Task:
        return Task(
            config=self.tasks_config["itinerary_compilation_task"],
            agent=self.itinerary_planner(),
            output_json=Itinerary
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SurpriseTravel Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2,
        )
