import os

import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4o-mini",
    instructions="Format your answer in Markdown.",
    input="Say hello in Hebrew and list 3 tips for learning Python.",
)

print(response.output_text)
print("input_tokens:", response.usage.input_tokens)
print("output_tokens:", response.usage.output_tokens)
