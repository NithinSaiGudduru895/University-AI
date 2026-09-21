from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

def generate_answer(question, results, university):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    context = []
    for i, item in enumerate(results, 1):
        location = item["file"]
        if item.get("page"):
            location += f", page {item['page']}"
        context.append(f"[SOURCE {i}: {location}]\n{item['text']}")

    prompt = f"""
You are the official-document RAG assistant for {university['name']}.

Answer the user's question using ONLY the retrieved source context.
Do not use outside knowledge.
Do not invent dates, fees, rules, eligibility, contacts, rankings or policies.
If the context is insufficient, say exactly:
"I couldn't find enough information in the indexed official documents."

Give a direct answer first, then a short source note when useful.
The sources are retrieved from documents associated with this university.

USER QUESTION:
{question}

RETRIEVED OFFICIAL-DOCUMENT CONTEXT:
{"".join(chr(10) + x + chr(10) for x in context)}
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    return (response.text or "").strip()
