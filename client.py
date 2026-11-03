import os

import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4.1-nano"
INSTRUCTIONS = "You are a helpful assistant. Format your answers in Markdown."


def ask_model(messages: list[dict]):
    stream = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=messages,
        stream=True,
    )
    for event in stream:
        if event.type == "response.output_text.delta":
            yield {"type": "delta", "delta": event.delta}
        elif event.type == "response.completed":
            usage = event.response.usage
            yield {
                "type": "usage",
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            }
