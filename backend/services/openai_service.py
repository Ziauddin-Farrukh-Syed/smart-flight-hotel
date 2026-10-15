from openai import OpenAI

from backend.config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


client = OpenAI(api_key=OPENAI_API_KEY)


def ask_openai(message: str) -> str:
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=message,
    )

    return response.output_text