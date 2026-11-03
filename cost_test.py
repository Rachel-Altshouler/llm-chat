from client import client, MODEL, INSTRUCTIONS

# Price in dollars per 1M tokens - check https://openai.com/api/pricing before relying on it
PRICE_INPUT = 10.00
PRICE_CACHED_INPUT = 1.00
PRICE_OUTPUT = 50.00

QUESTIONS = [
    "שלום, מה שלומך?",
    "ספר לי עובדה מעניינת על החלל.",
    "למה השמיים כחולים?",
    "תן לי רעיון לארוחת ערב מהירה.",
    "מה ההבדל בין מזג אוויר לאקלים?",
    "הסבר מה זה סטרימינג בצורה פשוטה.",
    "כתוב שיר קצר על הים.",
    "מה בירת אוסטרליה?",
    "תן לי טיפ אחד ללמידה יעילה.",
    "תודה, להתראות!",
]


def cost_of(usage) -> float:
    cached = usage.input_tokens_details.cached_tokens
    return (
        (usage.input_tokens - cached) * PRICE_INPUT
        + cached * PRICE_CACHED_INPUT
        + usage.output_tokens * PRICE_OUTPUT
    ) / 1_000_000


# The full history is sent every time, exactly like the chat page does
messages = []
total_in = total_cached = total_out = 0
total_cost = 0.0

print(f"{'#':>2} {'input':>7} {'cached':>7} {'output':>7} {'cost $':>10}")
for i, question in enumerate(QUESTIONS, start=1):
    messages.append({"role": "user", "content": question})
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=messages,
    )
    messages.append({"role": "assistant", "content": response.output_text})

    usage = response.usage
    cached = usage.input_tokens_details.cached_tokens
    cost = cost_of(usage)

    total_in += usage.input_tokens
    total_cached += cached
    total_out += usage.output_tokens
    total_cost += cost
    print(f"{i:>2} {usage.input_tokens:>7} {cached:>7} {usage.output_tokens:>7} {cost:>10.5f}")

print("-" * 38)
print(f"{'Σ':>2} {total_in:>7} {total_cached:>7} {total_out:>7} {total_cost:>10.5f}")
print(f"Average per message: ${total_cost / len(QUESTIONS):.5f}")
