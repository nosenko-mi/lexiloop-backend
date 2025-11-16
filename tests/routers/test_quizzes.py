import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.service.auth.dependencies import get_current_user_or_api_key
from app.domain.quiz import ContextQuiz
from app.domain.answer import ContextAnswer

# --- Setup Mock Auth ---
@pytest.fixture
def mock_auth(client, test_user):
    def override():
        return test_user
    app.dependency_overrides[get_current_user_or_api_key] = override
    yield
    app.dependency_overrides = {}

# --- Standard Test Data ---
SAMPLE_TEXT = (
    "Alice was beginning to get very tired of sitting by her sister on the bank, "
    "and of having nothing to do. Once or twice she had peeped into the book her sister was reading, "
    "but it had no pictures or conversations in it. 'And what is the use of a book,' "
    "thought Alice 'without pictures or conversation?'"
)

SAMPLE_SENTENCES = [
    "Alice was beginning to get very tired of sitting by her sister on the bank.",
    "Once or twice she had peeped into the book her sister was reading.",
    "'And what is the use of a book,' thought Alice."
]

# --- Tests for Local NLP Strategies (Running them for real) ---

@pytest.mark.parametrize("endpoint, payload_type", [
    ("/api/quizzes/simple/from-text", "simple"),
    ("/api/quizzes/sequence/from-text", "sequence"),
])
def test_local_strategies_contract(client, mock_auth, endpoint, payload_type):
    """
    Tests that local NLP strategies return a valid response within the requested limit.
    """
    LIMIT = 3
    payload = {
        "input": SAMPLE_TEXT,
        "limit": LIMIT,
        "number_of_answers": 4,
        "type": payload_type,
        "language": "en"
    }

    response = client.post(endpoint, json=payload)

    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    
    assert "quizzes" in data
    assert 0 <= len(data["quizzes"]) <= LIMIT
    
    if data["quizzes"]:
        first_quiz = data["quizzes"][0]
        assert first_quiz["type"] == payload_type
        assert len(first_quiz["answers"]) > 0

def test_session_quiz_generation(client, mock_auth):
    """
    Tests the session endpoint which combines simple and sequence quizzes.
    """
    LIMIT = 5
    payload = {
        "input_sentences": SAMPLE_SENTENCES,
        "limit": LIMIT,
        "number_of_answers": 4
    }

    response = client.post("/api/quizzes/session/from-text", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert 0 <= len(data["quizzes"]) <= LIMIT

# --- Tests for LLM Strategies (Mocked) ---

@patch("app.api.routers.quizzes.ContextQuizStrategyLLM")
def test_context_quiz_llm_mocked(MockStrategyClass, client, mock_auth):
    """
    Verifies router handles Context Quiz domain objects correctly.
    """
    mock_strategy_instance = MockStrategyClass.return_value
    
    fake_quiz = ContextQuiz(
        text="Why did Alice peep into the book?",
        explanation="Because she was bored.",
        identified_grammar="Past continuous",
        answers=[
            ContextAnswer(text="She was tired.", is_correct=False, reasoning="Distractor 1"),
            ContextAnswer(text="She was bored.", is_correct=True, reasoning="Correct answer reasoning"),
            ContextAnswer(text="She wanted pictures.", is_correct=False, reasoning="Distractor 2"),
            ContextAnswer(text="Her sister asked her.", is_correct=False, reasoning="Distractor 3"),
        ]
    )
    
    mock_strategy_instance.generate_many = AsyncMock(return_value=[fake_quiz, fake_quiz])

    payload = {
        "input": SAMPLE_TEXT,
        "limit": 2,
        "native_language": "es",
        "quiz_type": "grammar_mimicry",
        "language": "en" # FIXED: Added missing required field
    }
    
    response = client.post("/api/quizzes/context/from-text", json=payload)

    # If this fails with 422, print response.text to see exactly which field is missing
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert len(data["quizzes"]) == 2
    assert data["quizzes"][0]["type"] == "context"
    assert data["quizzes"][0]["text"] == "Why did Alice peep into the book?"
    assert data["quizzes"][0]["explanation"] == "Because she was bored."

@patch("app.api.routers.quizzes.ContextQuizStrategyLLM")
def test_context_quiz_returns_400_if_empty(MockStrategyClass, client, mock_auth):
    """
    Verifies that if the strategy returns an empty list (valid input, but no quiz generated),
    we get a 400 error.
    """
    mock_strategy_instance = MockStrategyClass.return_value
    mock_strategy_instance.generate_many = AsyncMock(return_value=[])

    payload = {
        "input": "This input is now long enough to pass the validator.",
        "limit": 1,
        "native_language": "es",
        "language": "en",
        "quiz_type": "grammar_mimicry",
        "number_of_answers": 4
    }
    
    response = client.post("/api/quizzes/context/from-text", json=payload)

    assert response.status_code == 400
    assert "Could not identify a testable grammatical structure" in response.json()["detail"]