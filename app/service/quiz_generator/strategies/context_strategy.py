import asyncio
import logging
from typing import List, cast
from app.service.quiz_generator.generator_strategy import QuizGenerationStrategy
from app.service.llm.config import LLM_MODEL, client as default_client
from app.service.llm import prompts
from app.service.llm.models import MultipleContextQuizResponse, SingleContextQuizResponse
from app.domain.quiz import AbstractQuiz, ContextQuiz
from app.domain.answer import ContextAnswer

logger = logging.getLogger(__name__)

class ContextQuizStrategyLLM(QuizGenerationStrategy):
    """
    A strategy for generating context-based grammar quizzes using an LLM.
    
    This strategy is focusing on grammatical patterns found in user-selected text.
    """
    
    def __init__(self, target_language: str, native_language: str, client=default_client) -> None:
        self.client = client
        self.target_language = target_language
        self.native_language = native_language

    async def generate_many(
        self,
        source: str,
        quiz_limit: int,
        answer_limit: int
    ) -> List[AbstractQuiz]:
        """
        Generates a list of context quizzes by making a single, structured
        call to an LLM.

        Args:
            source: The user-highlighted text.
            quiz_limit: The number of quizzes to generate.
            answer_limit: The number of answers per quiz.

        Returns:
            A list of ContextQuiz domain objects.
        """
        prompt = prompts.generate_context_quiz_prompt(
            source_text=source,
            quiz_limit=quiz_limit,
            answer_limit=answer_limit,
            user_native_language=self.native_language,
            target_language=self.target_language
        )

        try:
            response = await self.client.beta.chat.completions.parse(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format=MultipleContextQuizResponse,
                max_tokens=4096,
            )
            
            quizzes_response = response.choices[0].message.parsed
            if not quizzes_response or not quizzes_response.quizzes:
                logger.warning("LLM response was empty or malformed for context quiz.")
                return []
            
            domain_quizzes: List[AbstractQuiz] = []
            for quiz_data in quizzes_response.quizzes:
                
                domain_answers = [
                    ContextAnswer(
                        text=ans.text,
                        is_correct=ans.is_correct,
                        reasoning=ans.reasoning
                    ) for ans in quiz_data.answers
                ]
                
                domain_quiz = ContextQuiz(
                    text=quiz_data.text,
                    explanation=quiz_data.explanation,
                    identified_grammar=quiz_data.identified_grammar,
                    answers=domain_answers
                )
                
                logger.warning([a.__dict__ for a in domain_answers])
                if domain_quiz.is_valid():
                    domain_quizzes.append(domain_quiz)
                else:
                    logger.warning(f"Generated context quiz is not valid: {quiz_data.text}")
            
            return domain_quizzes

        except Exception as e:
            logger.error(f"Context quiz generation failed: {e}")
            return []

    async def generate_single(
        self, 
        source: str, 
        answer_limit: int
    ) -> AbstractQuiz | None:
        """
        Generates a single context quiz from a source sentence.
        """
        prompt = prompts.generate_single_context_quiz_prompt(
            source_text=source,
            answer_limit=answer_limit,
            user_native_language=self.native_language,
            target_language=self.target_language
        )
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format=SingleContextQuizResponse,
                max_tokens=2048
            )
            
            quiz_data = response.choices[0].message.parsed
            if not quiz_data:
                logger.warning("LLM response was empty or malformed for single context quiz.")
                return None

            domain_answers = [
                ContextAnswer(
                    text=ans.text,
                    is_correct=ans.is_correct,
                        reasoning=ans.reasoning
                ) for ans in quiz_data.answers
            ]
            
            domain_quiz = ContextQuiz(
                text=quiz_data.text,
                explanation=quiz_data.explanation,
                identified_grammar=quiz_data.identified_grammar,
                answers=domain_answers
            )
            
            if domain_quiz.is_valid():
                return domain_quiz
            else:
                logger.warning(f"Generated single context quiz is not valid: {quiz_data.text}")
                return None

        except Exception as e:
            logger.error(f"Single context quiz generation failed: {e}")
            return None


