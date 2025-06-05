import re


def split_into_sentences(text: str) -> list[str]:
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?";]) +', text)
    return sentences
