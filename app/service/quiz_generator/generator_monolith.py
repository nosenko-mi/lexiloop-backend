from app.service.quiz_builder.quiz_builder import AbstractQuizBuilder
from app.service.quiz_generator import verbs
from app.domain.quiz import SequenceQuiz, SingleAnswerQuiz
from app.domain.answer import SequenceAnswer, SimpleAnswer

import random
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')


class QuizGenerator:

    def __init__(self) -> None:
        self.verb_tags = verbs.verb_tags

    def generate_single_grammar(self, source: str, number_or_answers=4) -> SingleAnswerQuiz | None:
        print("=== generate_single_grammar ===")
        tokens = nltk.word_tokenize(source)
        pos_tags = nltk.pos_tag(tokens)

        verb_tags = [(idx, value) for idx, value in enumerate(
            pos_tags) if pos_tags[idx][1] in self.verb_tags]
        print(verb_tags)

        if not verb_tags:
            return None

        extracted = random.choice(verb_tags)
        if (verbs.check_negative(extracted[0], pos_tags)):
            extracted, pos_tags = verbs.convert_verb_to_negative(
                extracted[0], pos_tags)

        pos_tags[extracted[0]] = ("_", extracted[1][1])

        new_answers = self.__generate_answers(number_or_answers, extracted[1])

        quiz_text = ' '.join([t[0] for t in pos_tags])
        correct_answer = SimpleAnswer(text=extracted[1][0], is_correct=True)

        all_answers = [correct_answer]
        for a in new_answers:
            all_answers.append(SimpleAnswer(text=a, is_correct=False))

        return SingleAnswerQuiz(text=quiz_text, answers=all_answers)

    def generate_sequence(self, source: str, max_sequence_length: int = 5) -> SequenceQuiz:
        print("=== generate_sequence ===")

        # Always split the source into individual words
        fragments = nltk.word_tokenize(source)
        print(fragments)
        if len(fragments) > max_sequence_length:
            # Select a random subsequence to blank out
            max_len = min(max_sequence_length, len(fragments))
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


    def generate_voice(self):
        pass

    def generate_context(self):
        pass

    def __generate_answers(self, number_of_answers: int, correct_answer: tuple) -> list[str]:
        print("=== __generate_answers ===")

        correct_verb = correct_answer[0]
        correct_tense_tag = correct_answer[1]

        possible_tenses = self.verb_tags[:]  # fastest way to copy
        possible_tenses.remove(correct_tense_tag)

        new_tags = []
        new_verbs = []
        i = 1
        while i <= number_of_answers and len(possible_tenses) > 0:
            tag = random.choice(possible_tenses)
            is_equal, new_verb = verbs.generate_tense_from_tag(
                tag, correct_verb)

            if not is_equal and new_verb not in new_verbs:
                new_tags.append(tag)
                new_verbs.append(new_verb)

            possible_tenses.remove(tag)
            # print(f"Left possible tenses: {possible_tenses}")
            i += 1

        return new_verbs

