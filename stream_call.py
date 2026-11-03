import os

import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

stream = client.responses.create(
    model="gpt-6-astra",
    input="Write a short paragraph in Hebrew about the sea.",
    stream=True,
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.completed":
        print()
    elif event.type == "error":
        print("\nError:", event.message)

