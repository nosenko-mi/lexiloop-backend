import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

LLM_API = os.getenv("LLM_API", "http://localhost:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Llama-3.2-1B-Instruct")
OPENAI_KEY = os.getenv("OPENAI_KEY", "some_key")

print(LLM_API)

# client = AsyncOpenAI(
#     base_url=LLM_API,
#     api_key="empty"
# )

client = AsyncOpenAI(
    api_key=OPENAI_KEY
)