from abc import ABC, abstractmethod
import random

import nltk


from app.domain.answer import SequenceAnswer, SimpleAnswer
from app.domain.quiz import AbstractQuiz, SequenceQuiz, SingleAnswerQuiz
from app.service.quiz_generator.tokenizer import Tokenizer
from app.utils.text_utils import split_into_sentences
from app.utils.verb_utils import generate_tense_from_tag, verb_tags, check_negative, convert_verb_to_negative


class QuizGenerationStrategy(ABC):

    @abstractmethod
    def generate_single(self, source: str, answer_limit: int) -> AbstractQuiz | None:
        pass

    @abstractmethod
    def generate_many(self, source: str, quiz_limit: int, answer_limit: int) -> list[AbstractQuiz]:
        pass


class SimpleQuizStrategy(QuizGenerationStrategy):

    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def generate_single(self, source: str, answer_limit: int) -> AbstractQuiz | None:
        tokens = self.tokenizer.tokenize(source)
        pos_tags = nltk.pos_tag(tokens)

        verbs = [(idx, value) for idx, value in enumerate(
            pos_tags) if pos_tags[idx][1] in verb_tags]
        print(verbs)

        if not verbs:
            return None

        extracted = random.choice(verbs)
        if (check_negative(extracted[0], pos_tags)):
            extracted, pos_tags = convert_verb_to_negative(
                extracted[0], pos_tags)

        pos_tags[extracted[0]] = ("_", extracted[1][1])

        new_answers = self.__generate_answers(answer_limit, extracted[1])

        quiz_text = ' '.join([t[0] for t in pos_tags])
        correct_answer = SimpleAnswer(text=extracted[1][0], is_correct=True)

        all_answers = [correct_answer]
        for a in new_answers:
            all_answers.append(SimpleAnswer(text=a, is_correct=False))

        return SingleAnswerQuiz(text=quiz_text, answers=all_answers)
    

    def generate_many(self, source: str, quiz_limit: int, answer_limit: int) -> list[AbstractQuiz]:
        sentences = split_into_sentences(source)
        print(sentences)
        used_sentences = set()
        quizzes: list[AbstractQuiz] = []

        while len(quizzes) < quiz_limit and len(used_sentences) < len(sentences):
            text = random.choice([s for s in sentences if s not in used_sentences])

            quiz = self.generate_single(text, answer_limit)
            if quiz and quiz.is_valid():
                quizzes.append(quiz)
                used_sentences.add(text)

        return quizzes

    def __generate_answers(self, number_of_answers: int, correct_answer: tuple) -> list[str]:
        print("=== __generate_answers ===")

        correct_verb = correct_answer[0]
        correct_tense_tag = correct_answer[1]

        possible_tenses = verb_tags[:]  # fastest way to copy

        print(f"correct_verb: {correct_verb}, correct_tense_tag: {correct_tense_tag}, possible_tenses {possible_tenses}")
        possible_tenses.remove(correct_tense_tag)

        new_tags = []
        new_verbs = []
        i = 1
        while i < number_of_answers and len(possible_tenses) > 0:
            tag = random.choice(possible_tenses)
            is_equal, new_verb = generate_tense_from_tag(
                tag, correct_verb)

            if not is_equal and new_verb not in new_verbs:
                new_tags.append(tag)
                new_verbs.append(new_verb)

            possible_tenses.remove(tag)
            i += 1

        return new_verbs


class SequenceQuizStrategy(QuizGenerationStrategy):

    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer


    def generate_single(self, source: str, answer_limit: int) -> AbstractQuiz | None:
        print("=== generate_sequence ===")

        # Always split the source into individual words
        fragments = self.tokenizer.tokenize(source)
        print(fragments)
        if len(fragments) > answer_limit:
            # Select a random subsequence to blank out
            max_len = min(answer_limit, len(fragments))
            seq_len = random.randint(3, max_len)
            start_idx = random.randint(0, len(fragments) - seq_len)
            end_idx = start_idx + seq_len

            missing_seq = fragments[start_idx:end_idx]
            question_fragments = fragments[:start_idx] + ['_' for _ in missing_seq] + fragments[end_idx:]

            question_text = ' '.join(question_fragments)
            print(f"Question text: {question_text}")
            print(f"Correct sequence: {missing_seq}")

            all_answers = []
            for idx, frag in enumerate(missing_seq):
                all_answers.append(SequenceAnswer(text=frag, correct_position=idx))

        else:
            # Default behavior: reorder entire fragment list
            original_fragments = [(i, frag) for i, frag in enumerate(fragments)]
            shuffled = original_fragments[:]
            random.shuffle(shuffled)

            question_text = " ".join(["_" for f in original_fragments])
            all_answers = []
            for original_position, fragment in shuffled:
                all_answers.append(SequenceAnswer(text=fragment, correct_position=original_position))

        quiz = SequenceQuiz(text=question_text, answers=all_answers)
        return quiz


    def generate_many(self, source: str, quiz_limit: int, answer_limit: int) -> list[AbstractQuiz]:
        sentences = [s.strip() for s in source.split('.') if s.strip()]
        used_sentences = set()
        quizzes: list[AbstractQuiz] = []

        while len(quizzes) < quiz_limit and len(used_sentences) < len(sentences):
            text = random.choice([s for s in sentences if s not in used_sentences])

            quiz = self.generate_single(text, answer_limit)
            if quiz and quiz.is_valid():
                quizzes.append(quiz)
                used_sentences.add(text)

        return quizzes


