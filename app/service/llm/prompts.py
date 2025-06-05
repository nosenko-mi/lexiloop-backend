

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
