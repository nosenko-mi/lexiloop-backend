import asyncio
import random
from typing import List
from pydantic import ValidationError
from app.service.quiz_generator.generator_strategy import QuizGenerationStrategy
from app.service.llm.config import LLM_MODEL, client
from app.service.llm import prompts
from app.service.llm.models import MultipleSimpleQuizResponse, SimpleAnswerResponse, SingleSimpleQuizResponse
from app.domain.quiz import AbstractQuiz, SingleAnswerQuiz, SimpleAnswer





class SimpleQuizStrategyLLM(QuizGenerationStrategy):
    async def generate_single(self, source: str, answer_limit: int) -> AbstractQuiz | None:
        prompt = prompts.generate_single_grammar_prompt(source, answer_limit)

        try:

            response = await client.beta.chat.completions.parse(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format=SingleSimpleQuizResponse,
                max_tokens=4096,
            )
            quiz_response = response.choices[0].message.parsed
            
            if not quiz_response:
                return None
            
            return SingleAnswerQuiz(text=quiz_response.text, answers=[SimpleAnswer(text=a.text, is_correct=a.is_correct) for a in quiz_response.answers])
            
            response = await client.responses.parse(
                model=LLM_MODEL,
                input=[{"role": "user", "content": prompt}],
                temperature=0.5,
                text_format=SingleSimpleQuizResponse
            )
            print(response)
            for output in response.output:
                if output.type != "message":
                    raise Exception("Unexpected non message")

                for item in output.content:
                    if item.type != "output_text":
                        raise Exception("unexpected output type")

                    if not item.parsed:
                        raise Exception("Could not parse response")


                    print("parsed: ", item.parsed)

                    quiz = item.parsed

                    return SingleAnswerQuiz(text=quiz.text, answers=[SimpleAnswer(text=a.text, is_correct=a.is_correct) for a in quiz.answers])
            
            return None
        except Exception as e:
            print(f"Quiz generation failed: {e}")
            return None


    async def generate_many(self, source: str, quiz_limit: int, answer_limit: int) -> List[AbstractQuiz]:
        sentences = [s.strip() for s in source.split('.') if s.strip()]
        if not sentences:
            return []

        random.shuffle(sentences)
        candidate_sentences = sentences[:quiz_limit]

        tasks = [asyncio.create_task(self.generate_single(s, answer_limit)) for s in candidate_sentences]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        quizzes: List[AbstractQuiz] = []
        for quiz in results:
            if isinstance(quiz, BaseException):
                continue
            if quiz and quiz.is_valid():
                quizzes.append(quiz)

        return quizzes

    # async def generate_many(self, source: str, quiz_limit: int, answer_limit: int) -> list[AbstractQuiz]:
    #     prompt = prompts.generate_many_grammar_prompt(source, quiz_limit, answer_limit)

    #     try:
    #         response = await client.beta.chat.completions.parse(
    #             model=LLM_MODEL,
    #             messages=[{"role": "user", "content": prompt}],
    #             temperature=0.5,
    #             response_format=MultipleSimpleQuizResponse, # type: ignore
    #             max_tokens=4096,  # Adjust as needed
    #         )
    #         quizzes_response = response.choices[0].message.parsed
    #         quizzes = []
    #         if not quizzes_response:
    #             return quizzes
            
    #         for quiz in quizzes_response.quizzes:
    #             quizzes.append(
    #                 SingleAnswerQuiz(text=quiz.text, answers=[SimpleAnswer(text=a.text, is_correct=a.is_correct) for a in quiz.answers])
    #             )
    #         return quizzes

    #     except Exception as e:
    #         print(f"Quiz generation failed: {e}")
    #         return []

