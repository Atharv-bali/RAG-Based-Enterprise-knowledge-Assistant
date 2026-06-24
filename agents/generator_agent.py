import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3.2"


def generate_answer(
    question,
    context
):

    prompt = f"""
You are an enterprise assistant.

Answer ONLY using supplied context.

If information is unavailable,
say "I do not know."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]