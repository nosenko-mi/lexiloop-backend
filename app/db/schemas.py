from pydantic import BaseModel, ConfigDict
from typing import List

class SimpleAnswerBase(BaseModel):
    text: str
    is_correct: bool


class SimpleAnswerCreate(SimpleAnswerBase):
    pass


class SimpleAnswer(SimpleAnswerBase):
    id: int
    quiz_id: int

    class ConfigDict:
        from_attributes = True


class SequenceAnswerBase(BaseModel):
    text: str
    position: int


class SequenceAnswerCreate(SequenceAnswerBase):
    pass


class SequenceAnswer(SequenceAnswerBase):
    id: int
    quiz_id: int

    class ConfigDict:
        from_attributes = True

class ContextAnswerBase(BaseModel):
    text: str
    is_correct: bool
    reasoning: str


class ContextAnswerCreate(ContextAnswerBase):
    pass


class ContextAnswer(ContextAnswerBase):
    id: int
    quiz_id: int

    class ConfigDict:
        from_attributes = True

class SimpleQuizBase(BaseModel):
    text: str
    type_id: int


class SimpleQuizCreate(SimpleQuizBase):
    pass


class SimpleQuiz(SimpleQuizBase):
    id: int
    answers: list[SimpleAnswer] = []

    class ConfigDict:
        from_attributes = True


class SequenceQuizBase(BaseModel):
    text: str
    type_id: int


class SequenceQuizCreate(SequenceQuizBase):
    pass


class SequenceQuiz(SequenceQuizBase):
    id: int
    answers: list[SequenceAnswer] = []

    class ConfigDict:
        from_attributes = True


class VoiceQuizBase(BaseModel):
    text: str
    expected_text: str
    type_id: int


class VoiceQuizCreate(VoiceQuizBase):
    pass


class VoiceQuiz(VoiceQuizBase):
    id: int

    class ConfigDict:
        from_attributes = True


class ContextQuizBase(BaseModel):
    text: str
    explanation: str
    identified_grammar: str
    type_id: int

class ContextQuizCreate(ContextQuizBase):
    pass


class ContextQuiz(ContextQuizBase):
    id: int
    answers: list[ContextAnswer] = []

    class ConfigDict:
        from_attributes = True
        

class TextFeatureBase(BaseModel):
    text: str


class TextFeatureCreate(TextFeatureBase):
    dataset_id: int


class TextFeature(TextFeatureBase):
    id: int
    dataset_id: int

    class ConfigDict:
        from_attributes = True


class DatasetBase(BaseModel):
    title: str
    source: str


class DatasetCreate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: int
    entries: list[TextFeature] = []

    class ConfigDict:
        from_attributes = True


class UserSettingsBase(BaseModel):
    """Base schema with common fields."""
    native_language_code: str
    target_language_code: str

class UserSettingsCreate(UserSettingsBase):
    """Schema used for creating or updating settings."""
    pass

class UserSettings(UserSettingsBase):
    """Schema used for returning settings from the API."""
    user_id: int

    class ConfigDict:
        from_attributes = True
