import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import time
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent / "src")
)

from chatbot import (
    get_chatbot_response,
    retrieve_travel_records,
    retrieve_slang_records
)

tests = [
    (
        "Dataset route matching",
        "How do I get from San Francisco to Central Park using train?"
    ),
    (
        "Different question wording",
        "How can I travel between San Francisco and Central Park by rail?"
    ),
    (
        "Location spelling correction",
        "How do I get from San Fransisco to Central Park by train?"
    ),
    (
        "General travel knowledge",
        "What are the best places to visit in Japan?"
    ),
    (
        "Food recommendation",
        "What food should I try in Los Angeles?"
    ),
    (
        "Travel itinerary",
        "Plan a 3-day itinerary in San Francisco."
    ),
    (
        "Gen Z slang understanding",
        "Low key, what are the best places to visit in Japan?"
    ),
    (
        "Outside dataset transport",
        "How do I travel from Kuala Lumpur to Penang by train?"
    ),
    (
        "Missing route information",
        "When is the next train?"
    ),
    (
        "Unavailable schedule",
        "What time is the train from San Francisco to Central Park on 2099-12-31?"
    ),
    (
        "Hallucination prevention",
        "Invent a train departure schedule from Kuala Lumpur to Penang."
    ),
    (
        "Unrelated question",
        "Explain how to create a database table."
    )
]

results = []

for index, (name, question) in enumerate(tests, start=1):

    print("\n" + "=" * 60)
    print(f"TEST {index}: {name}")
    print("=" * 60)
    print("Question:", question)

    try:
        records = retrieve_travel_records(question)
        slang = retrieve_slang_records(question)

        print("Travel records:", len(records))
        print(
            "Detected slang:",
            [str(row["keyword"]) for row in slang]
        )

        start = time.perf_counter()

        answer = get_chatbot_response(question)

        duration = time.perf_counter() - start

        print("\nChatbot response:")
        print(answer)
        print(f"\nResponse time: {duration:.2f} seconds")

        errors = [
            "gemini api error",
            "unexpected error",
            "currently unavailable",
            "couldn't generate a response"
        ]

        success = (
            isinstance(answer, str)
            and bool(answer.strip())
            and not any(
                error in answer.lower()
                for error in errors
            )
        )

        status = "RESPONSE RECEIVED" if success else "ERROR"

        results.append(status)

        print("Execution status:", status)

    except Exception as e:
        results.append("ERROR")
        print("Execution status: ERROR")
        print(e)

    time.sleep(2)

print("\n" + "=" * 60)
print("END-TO-END TEST SUMMARY")
print("=" * 60)
print("Total tests:", len(tests))
print("Responses received:", results.count("RESPONSE RECEIVED"))
print("Errors:", results.count("ERROR"))
print("Content accuracy: Requires response review")
print("=" * 60)
