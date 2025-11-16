

# def generate_single_grammar_prompt(source: str, answers_limit: int) -> str:
#     return f"""
# Your task is to generate a single grammar quiz with {answers_limit} answer options each based on the following input text.

# Input text:
# {source}

# Return a JSON object in the following format:
# {{"quizzes": [{{"text": "...", "answers": [{{"text": "...", "is_correct": true}}, ...]}}]}}

# Only return valid JSON. Do not include explanations, comments, or markdown.

# Instructions:
# 1. Select a **single verb** and create a gap-fill (cloze) grammar question that focuses on verb tense.
# 2. Replace the chosen verb with the character **'_'** in the quiz sentence.
# """


from app.service.llm.models import MultipleContextQuizResponse, SingleContextQuizResponse
from app.service.llm.language_codes import LANGUAGE_CODES


def generate_single_grammar_prompt(source: str, answers_limit: int) -> str:
    return f"""
Your task is to generate one grammar quiz based on the input text.

Input text:
{source}

Instructions:
1. Select a single verb from one sentence in the input.
2. Replace that verb with the character '_' to create a gap-fill grammar quiz.
3. Create {answers_limit} unique answer options — only **one** should be grammatically correct in context.
4. Each answer must include a brief explanation in a "reasoning" field (1–2 short sentences).
5. All options should be realistic verb forms or conjugations.
6. Do not repeat the same answer multiple times.
7. Use only one sentence. Be concise.

Return the result as a valid JSON object in the following format:
{{
  "quizzes": [
    {{
      "text": "Sentence with _",
      "answers": [
        {{
          "text": "verb1",
          "is_correct": true,
          "reasoning": "Explain why this is correct in context."
        }},
        {{
          "text": "verb2",
          "is_correct": false,
          "reasoning": "Explain why this is grammatically incorrect or less appropriate."
        }},
        ...
      ]
    }}
  ]
}}

Only return the JSON — no explanations, markdown, or extra commentary.
"""


def generate_many_grammar_prompt(source: str, quiz_limit: int, answers_limit: int) -> str:
    return f"""
Your task is to generate {quiz_limit} grammar quiz questions with {answers_limit} answer options each based on the following input text.

Input text:
{source}

Return a JSON object in the following format:
{{"quizzes": [{{"text": "...", "answers": [{{"text": "...", "is_correct": true}}, ...]}}]}}

Only return valid JSON. Do not include explanations, comments, or markdown.

Instructions:
1. Use **one sentence per quiz**. If the number of sentences is less than {quiz_limit}, reuse sentences as needed.
2. Select a **single verb** and create a gap-fill (cloze) grammar question that focuses on verb tense.
3. Replace the chosen verb with the character **'_'** in the quiz sentence.
4. All verbs should be **unique across quizzes**.
5. Be concise — do not repeat or rephrase unnecessarily.
"""


def generate_single_context_quiz_prompt(
    source_text: str,
    answer_limit: int,
    user_native_language: str = "Ukrainian",
    target_language: str = "English"
) -> str:
    """
    Generates a prompt to create ONE advanced grammar-mimicry quiz.
    """
    native_lang_name = LANGUAGE_CODES.get(user_native_language, user_native_language)
    target_lang_name = LANGUAGE_CODES.get(target_language, target_language)
    return f"""
You are an expert {target_lang_name} language tutor creating a contextual grammar quiz for an adult L2 learner whose native language is {native_lang_name}. The user has selected a sentence from a text they are reading.

Your task is to analyze the source sentence and generate **one** high-quality, relevant grammar quiz.

**Source Sentence:**
"{source_text}"

**Instructions:**
1.  **Analyze and Choose:** First, carefully analyze the source text to find the most interesting and useful grammatical structure for an L2 learner. Choose the BEST quiz type from the following options:
    * **grammar_mimicry:** Test a specific tense, conditional, or complex clause structure.
    * **clause_connector:** Test understanding of conjunctions (e.g., despite, therefore, although).
    * **phrasal_verb:** Test the meaning of a phrasal verb found in the text.
    * **voice_transformation:** Test the ability to convert between active and passive voice.
2.  **Generate Quiz:** Create a new question that forces the user to apply the structure you identified.
3.  **Create Answers:** Create {answer_limit} answer choices. The correct answer must be the grammatically correct option. The incorrect answers should be plausible common mistakes that a {native_lang_name} speaker might make.
4.  **Explain:** Provide a concise, helpful explanation in {native_lang_name} for the correct answer.
5.  **Format:** Respond with ONLY a single, valid JSON object that follows the schema below.
6. Replace the chosen verb/phrase with exactly one underscore character (_) to create the gap-fill quiz question. Example: "She _ out of the house."

**JSON Output Schema:**
{SingleContextQuizResponse.model_json_schema()}

Ensure your quiz has exactly {answer_limit} answers.
"""


def generate_context_quiz_prompt(
    source_text: str,
    quiz_limit: int,
    answer_limit: int,
    user_native_language: str = "Ukrainian",
    target_language: str = "English"
) -> str:
    native_lang_name = LANGUAGE_CODES.get(user_native_language, user_native_language)
    target_lang_name = LANGUAGE_CODES.get(target_language, target_language)
    return f"""
You are an expert {target_lang_name} language tutor creating a contextual grammar quiz for an adult L2 learner whose native language is {native_lang_name}. The user has selected a sentence from a text they are reading.

Your task is to analyze the source text and generate {quiz_limit} high-quality, relevant grammar quizzes.

**Source Text:**
"{source_text}"

**Instructions:**
1.  **Analyze and Choose:** First, carefully analyze the source text to find the most interesting and useful grammatical structures for an L2 learner. Based on your analysis, choose the BEST quiz type from the following options for each quiz you generate:
    * **grammar_mimicry:** Test a specific tense, conditional, or complex clause structure.
    * **clause_connector:** Test understanding of conjunctions (e.g., despite, therefore, although).
    * **phrasal_verb:** Test the meaning of a phrasal verb found in the text.
    * **voice_transformation:** Test the ability to convert between active and passive voice.
2.  **Generate Quiz:** Create a new question that forces the user to apply the structure you identified.
3.  **Create Answers:** The correct answer must be the grammatically correct option. The incorrect answers should be plausible common mistakes that a {native_lang_name} speaker might make.
4.  **Explain:** Provide a concise, helpful explanation in {native_lang_name} for the correct answer.
5.  **Format:** Respond with ONLY a single, valid JSON object that follows the schema below.
6.  Replace the chosen verb/phrase with exactly one underscore character (_) to create the gap-fill quiz question. Example: "She _ out of the house."

**JSON Output Schema:**
{MultipleContextQuizResponse.model_json_schema()}

Ensure you generate exactly {quiz_limit} quizzes and each quiz has exactly {answer_limit} answers.
"""