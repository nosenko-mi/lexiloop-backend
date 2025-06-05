from pydantic import BaseModel


class SimpleAnswerBase(BaseModel):
    text: str
    is_correct: bool


class SimpleAnswerCreate(SimpleAnswerBase):
    pass


class SimpleAnswer(SimpleAnswerBase):
    id: int
    quiz_id: int

    class Config:
        from_attribues = True


class SequenceAnswerBase(BaseModel):
    text: str
    position: int


class SequenceAnswerCreate(SequenceAnswerBase):
    pass


class SequenceAnswer(SequenceAnswerBase):
    quiz_id: int

    class Config:
        from_attribues = True


class SimpleQuizBase(BaseModel):
    text: str
    type_id: int


class SimpleQuizCreate(SimpleQuizBase):
    pass


class SimpleQuiz(SimpleQuizBase):
    id: int
    answers: list[SimpleAnswer] = []

    class Config:
        from_attribues = True


class SequenceQuizBase(BaseModel):
    text: str
    type_id: int


class SequenceQuizCreate(SequenceQuizBase):
    pass


class SequenceQuiz(SequenceQuizBase):
    id: int
    answers: list[SequenceAnswer] = []

    class Config:
        from_attribues = True


class VoiceQuizBase(BaseModel):
    text: str
    expected_text: str
    type_id: int


class VoiceQuizCreate(VoiceQuizBase):
    pass


class VoiceQuiz(VoiceQuizBase):
    id: int

    class Config:
        from_attribues = True


class TextFeatureBase(BaseModel):
    text: str


class TextFeatureCreate(TextFeatureBase):
    dataset_id: int


class TextFeature(TextFeatureBase):
    id: int
    dataset_id: int

    class Config:
        from_attribues = True


class DatasetBase(BaseModel):
    title: str
    source: str


class DatasetCreate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: int
    entries: list[TextFeature] = []

    class Config:
        from_attribues = True