import os

# Use the Windows certificate store (needed behind NetFree's SSL filtering)
import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")

client = OpenAI(api_key=api_key)

MODEL = "gpt-6-astra"
INSTRUCTIONS = (
    "You are a helpful assistant. Format your answers in Markdown: "
    "use headings, **bold**, bullet lists, tables and code blocks where they help."
)


def ask_model(messages: list[dict]):
    """Stream the model's answer, yielding a "delta" event per text chunk
    and a final "usage" event with the token counts."""
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
