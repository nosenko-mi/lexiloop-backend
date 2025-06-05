from abc import abstractmethod
from typing import Protocol
import nltk


class Tokenizer(Protocol):

    @abstractmethod
    def tokenize(self, text: str) -> list[str]:
        pass


class EnglishTokenizer:
    def tokenize(self, text: str) -> list[str]:
        return nltk.word_tokenize(text)
