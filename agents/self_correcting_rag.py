from retrieval.hybrid_retrieval import (
    hybrid_search
)

from generator_agent import (
    generate_answer
)

from evaluator_agent import (
    evaluate_answer
)

MAX_RETRIES = 3


def ask(question):

    dense_top_k = 20

    bm25_top_k = 20

    for attempt in range(
        MAX_RETRIES
    ):

        print(
            f"\nAttempt {attempt+1}"
        )

        retrieval = hybrid_search(
            query=question,
            dense_top_k=dense_top_k,
            bm25_top_k=bm25_top_k
        )

        context = retrieval[
            "context"
        ]

        answer = generate_answer(
            question,
            context
        )

        print(
            "\nGenerated Answer:\n"
        )

        print(answer)

        verdict = evaluate_answer(
            question,
            context,
            answer
        )

        print(
            "\nEvaluation:",
            verdict
        )

        if verdict == "PASS":

            return {
                "status": "PASS",
                "answer": answer
            }

        print(
            "\nExpanding retrieval..."
        )

        dense_top_k += 10
        bm25_top_k += 10

    return {
        "status":
        "FAILED_AFTER_RETRIES",
        "answer": answer
    }

if __name__ == "__main__":

    question = (
        "What was Q3 revenue growth?"
    )

    result = ask(
        question
    )

    print("\n")
    print("=" * 80)

    print(
        result["status"]
    )

    print("\n")

    print(
        result["answer"]
    )