import nltk

from app.db import schemas
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')


class Answer:

    def __init__(self, text: str, is_correct: bool) -> None:
        self.text = text
        self.is_correct = is_correct

    def equals(self, x) -> bool:
        return self.text == x.text

    def __str__(self) -> str:
        return f"{self.text} [correct={self.is_correct}]"


class Quiz:

    def __init__(self) -> None:
        self.text: str = ""
        self.answers: list[Answer] = []
        self.type: int = type

    def set_question(self, text: str) -> None:
        self.text = text

    def add_answer(self, answer: Answer) -> None:
        self.answers.append(answer)

    def is_valid(self) -> bool:
        correct_num = sum(a.is_correct for a in self.answers)
        contains_none = False
        for a in self.answers:
            if a.text is None: 
                contains_none = True
                break
        return correct_num >= 1 and not contains_none and self.text is not None

    def get_correct_answers(self) -> list[Answer]:
        if self.is_valid():
            return [a for a in self.answers if a.is_correct]
        else:
            return []

    def __str__(self) -> str:
        res = f"{self.text}\n"
        for i, a in enumerate(self.answers):
            res += f"{i+1}. {a}\n"
        return res
    
    def to_create_schema(self) -> tuple[schemas.SimpleQuizCreate, list[schemas.SimpleAnswerCreate]]:
        quiz = schemas.SimpleQuizCreate(text=self.text, type_id=self.type)
        answers = [schemas.SimpleAnswerCreate(text=a.text, is_correct=a.is_correct) for a in self.answers]
        return (quiz, answers)


class SequenceQuiz:
    pass


class QuizException(Exception):
    pass


class QuizBuilder:

    def __init__(self) -> None:
        self.reset()

    def add_question(self, text: str):
        if text is None or len(text) < 6:
            raise Exception("Text is not valid. Either None or < 6 symbols")

        self.quiz.set_question(text)

    def create_question(self, tags: list[tuple]):
        # t[0] is a word part of expected tuple e.g ("word", "NN")
        text = ' '.join([t[0] for t in tags])

        self.quiz.set_question(text)

    def add_answer(self, answer: Answer):
        self.quiz.add_answer(answer)

    def set_type(self, type: int):
        self.quiz.type = type

    def build(self) -> Quiz:
        quiz = self.quiz
        self.reset()
        return quiz

    def reset(self):
        self.quiz = Quiz()


# class QuizGenerator:

#     def __init__(self, quiz_builder: QuizBuilder) -> None:
#         self.verb_tags = verbs.verb_tags
#         self.builder = quiz_builder

#     def generate_single_grammar(self, source: str, number_or_answers=4) -> Quiz:
#         tokens = nltk.word_tokenize(source)
#         pos_tags = nltk.pos_tag(tokens)

#         verb_tags = [(idx, value) for idx, value in enumerate(
#             pos_tags) if pos_tags[idx][1] in self.verb_tags]
#         print(verb_tags)

#         extracted = random.choice(verb_tags)
#         if (verbs.check_negative(extracted[0], pos_tags)):
#             extracted, pos_tags = verbs.convert_verb_to_negative(
#                 extracted[0], pos_tags)

#         pos_tags[extracted[0]] = ("_", extracted[1][1])

#         new_answers = self.__generate_answers(number_or_answers, extracted[1])

#         self.builder.create_question(pos_tags)
#         self.builder.add_answer(Answer(text=extracted[1][0], is_correct=True))
#         for a in new_answers:
#             self.builder.add_answer(Answer(text=a, is_correct=False))
#         quiz = self.builder.build()

#         return quiz

#     def generate_sequence(self, source: str):
#         pass


#     def generate_voice(self):
#         pass

#     def generate_context(self):
#         pass

#     def __generate_answers(self, number_of_answers: int, correct_answer: tuple) -> list[Answer]:

#         correct_verb = correct_answer[0]
#         correct_tense_tag = correct_answer[1]

#         possible_tenses = self.verb_tags[:]  # fastest way to copy
#         possible_tenses.remove(correct_tense_tag)

#         new_tags = []
#         new_verbs = []
#         i = 1
#         while i < number_of_answers and len(possible_tenses) > 0:
#             tag = random.choice(possible_tenses)
#             is_equal, new_verb = verbs.generate_tense_from_tag(
#                 tag, correct_verb)

#             if not is_equal:
#                 new_tags.append(tag)
#                 new_verbs.append(new_verb)

#             possible_tenses.remove(tag)
#             i += 1

#         return new_verbs



