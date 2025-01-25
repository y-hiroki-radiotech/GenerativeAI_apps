from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models import Persona, Personas, Interview, InterviewResult, EvaluationResult
from logger import logger

class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI, k: int = 5):
        self.llm = llm.with_structured_output(Personas)
        self.k = k

    def run(self, user_request: str) -> Personas:
        logger.debug("Generating personas")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはユーザーインタビュー用の多様なペルソナを作成する専門家です。",
                ),
                (
                    "human",
                    f"以下のユーザーリクエストに関するインタビュー用に、{self.k}人の多様なペルソナを生成してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n\n"
                    "各ペルソナには名前と簡単な背景を含めてください。年齢、性別、職業、技術的専門知識において多様性を確保してください。",
                ),
            ]
        )
        chain = prompt | self.llm
        personas = chain.invoke({"user_request": user_request})
        logger.debug(f"Generated personas: {personas}")
        return personas

class InterviewConductor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, user_request: str, personas: list[Persona]) -> InterviewResult:
        logger.debug("Conducting interviews")
        questions = self._generate_questions(user_request=user_request, personas=personas)
        answers = self._generate_answers(personas=personas, questions=questions)
        interviews = self._create_interviews(personas=personas, questions=questions, answers=answers)
        interview_result = InterviewResult(interviews=interviews)
        logger.debug(f"Conducted interviews: {interview_result}")
        return interview_result

    def _generate_questions(self, user_request: str, personas: list[Persona]) -> list[str]:
        question_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはユーザー要件に基づいて適切な質問を生成する専門家です。",
                ),
                (
                    "human",
                    "以下のペルソナに関連するユーザーリクエストについて、1つの質問を生成してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n"
                    "ペルソナ: {persona_name} - {persona_background}\n\n"
                    "質問は具体的で、このペルソナの視点から重要な情報を引き出すように設計してください。",
                ),
            ]
        )
        question_chain = question_prompt | self.llm | StrOutputParser()
        question_queries = [
            {
                "user_request": user_request,
                "persona_name": persona.name,
                "persona_background": persona.background,
            }
            for persona in personas
        ]
        questions = question_chain.batch(question_queries)
        logger.debug(f"Generated questions: {questions}")
        return questions

    def _generate_answers(self, personas: list[Persona], questions: list[str]) -> list[str]:
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは以下のペルソナとして回答しています: {persona_name} - {persona_background}",
                ),
                ("human", "質問: {question}"),
            ]
        )
        answer_chain = answer_prompt | self.llm | StrOutputParser()
        answer_queries = [
            {
                "persona_name": persona.name,
                "persona_background": persona.background,
                "question": question,
            }
            for persona, question in zip(personas, questions)
        ]
        answers = answer_chain.batch(answer_queries)
        logger.debug(f"Generated answers: {answers}")
        return answers

    def _create_interviews(self, personas: list[Persona], questions: list[str], answers: list[str]) -> list[Interview]:
        interviews = [
            Interview(persona=persona, question=question, answer=answer)
            for persona, question, answer in zip(personas, questions, answers)
        ]
        logger.debug(f"Created interviews: {interviews}")
        return interviews

class InformationEvaluator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(EvaluationResult)

    def run(self, user_request: str, interviews: list[Interview]) -> EvaluationResult:
        logger.debug("Evaluating information")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは包括的な要件文書を作成するための情報の十分性を評価する専門家です。",
                ),
                (
                    "human",
                    "以下のユーザーリクエストとインタビュー結果に基づいて、包括的な要件文書を作成するのに十分な情報が集まったかどうかを判断してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n\n"
                    "インタビュー結果:\n{interview_results}",
                ),
            ]
        )
        chain = prompt | self.llm
        evaluation_result = chain.invoke(
            {
                "user_request": user_request,
                "interview_results": "\n".join(
                    f"ペルソナ: {i.persona.name} - {i.persona.background}\n"
                    f"質問: {i.question}\n回答: {i.answer}\n"
                    for i in interviews
                ),
            }
        )
        logger.debug(f"Evaluation result: {evaluation_result}")
        return evaluation_result

class RequirementsDocumentGenerator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, user_request: str, interviews: list[Interview]) -> str:
        logger.debug("Generating requirements document")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは収集した情報に基づいて要件文書を作成する専門家です。",
                ),
                (
                    "human",
                    "以下のユーザーリクエストと複数のペルソナからのインタビュー結果に基づいて、要件文書を作成してください。\n\n"
                    "ユーザーリクエスト: {user_request}\n\n"
                    "インタビュー結果:\n{interview_results}\n"
                    "要件文書には以下のセクションを含めてください:\n"
                    "1. プロジェクト概要\n"
                    "2. 主要機能\n"
                    "3. 非機能要件\n"
                    "4. 制約条件\n"
                    "5. ターゲットユーザー\n"
                    "6. 優先順位\n"
                    "7. リスクと軽減策\n\n"
                    "出力は必ず日本語でお願いします。\n\n要件文書:",
                ),
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        requirements_doc = chain.invoke(
            {
                "user_request": user_request,
                "interview_results": "\n".join(
                    f"ペルソナ: {i.persona.name} - {i.persona.background}\n"
                    f"質問: {i.question}\n回答: {i.answer}\n"
                    for i in interviews
                ),
            }
        )
        logger.debug(f"Generated requirements document: {requirements_doc}")
        return requirements_doc
