import os

import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-6-astra",
    instructions="Format your answer in Markdown.",
    input="Say hello in Hebrew and list 3 tips for learning Python.",
)

print(response.output_text)
print()
print("input_tokens:", response.usage.input_tokens)
print("output_tokens:", response.usage.output_tokens)
#print(response.to_json())
print("good by")
