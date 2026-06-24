import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3.2"


def evaluate_answer(
    question,
    context,
    answer
):

    prompt = f"""
You are a strict evaluator.

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
{answer}

Check whether every statement
in the answer is supported by
the supplied context.

Respond ONLY with:

PASS

or

FAIL
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    verdict = response.json()[
        "response"
    ].strip()

    if "PASS" in verdict:
        return "PASS"

    return "FAIL"