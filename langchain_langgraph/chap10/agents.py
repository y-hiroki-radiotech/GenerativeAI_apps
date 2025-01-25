from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from models import InterviewState
from generators import PersonaGenerator, InterviewConductor, InformationEvaluator, RequirementsDocumentGenerator
from logger import logger
from typing import Optional, Any


class DocumentationAgent:
    def __init__(self, llm: ChatOpenAI, k: Optional[int] = None):
        self.persona_generator = PersonaGenerator(llm=llm, k=k)
        self.interview_conductor = InterviewConductor(llm=llm)
        self.information_evaluator = InformationEvaluator(llm=llm)
        self.requirements_generator = RequirementsDocumentGenerator(llm=llm)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(InterviewState)
        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("conduct_interviews", self._conduct_interviews)
        workflow.add_node("evaluate_information", self._evaluate_information)
        workflow.add_node("generate_requirements", self._generate_requirements)
        workflow.set_entry_point("generate_personas")
        workflow.add_edge("generate_personas", "conduct_interviews")
        workflow.add_edge("conduct_interviews", "evaluate_information")
        workflow.add_conditional_edges(
            "evaluate_information",
            lambda state: not state.is_information_sufficient and state.iteration < 5,
            {True: "generate_personas", False: "generate_requirements"},
        )
        workflow.add_edge("generate_requirements", END)
        return workflow.compile()

    def _generate_personas(self, state: InterviewState) -> dict[str, Any]:
        logger.debug("Generating personas in DocumentationAgent")
        new_personas: Personas = self.persona_generator.run(state.user_request)
        return {
            "personas": new_personas.personas,
            "iteration": state.iteration + 1,
        }

    def _conduct_interviews(self, state: InterviewState) -> dict[str, Any]:
        logger.debug("Conducting interviews in DocumentationAgent")
        new_interviews: InterviewResult = self.interview_conductor.run(
            state.user_request, state.personas[-5:]
        )
        return {"interviews": new_interviews.interviews}

    def _evaluate_information(self, state: InterviewState) -> dict[str, Any]:
        logger.debug("Evaluating information in DocumentationAgent")
        evaluation_result: EvaluationResult = self.information_evaluator.run(
            state.user_request, state.interviews
        )
        return {
            "is_information_sufficient": evaluation_result.is_sufficient,
            "evaluation_reason": evaluation_result.reason,
        }

    def _generate_requirements(self, state: InterviewState) -> dict[str, Any]:
        logger.debug("Generating requirements document in DocumentationAgent")
        requirements_doc: str = self.requirements_generator.run(
            state.user_request, state.interviews
        )
        return {"requirements_doc": requirements_doc}

    def run(self, user_request: str) -> str:
        logger.info("Running DocumentationAgent")
        initial_state = InterviewState(user_request=user_request)
        final_state = self.graph.invoke(initial_state)
        logger.info("Finished running DocumentationAgent")
        return final_state["requirements_doc"]
