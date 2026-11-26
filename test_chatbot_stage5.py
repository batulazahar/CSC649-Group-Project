import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent / "src")
)

from chatbot import (
    retrieve_travel_records,
    retrieve_slang_records,
    is_transport_question
)

tests = [
    {
        "name": "Exact route matching",
        "question": "How do I get from San Francisco to Central Park using train?",
        "expected": "route"
    },
    {
        "name": "Different question wording",
        "question": "How can I travel from San Francisco to Central Park by train?",
        "expected": "route"
    },
    {
        "name": "Transport synonym",
        "question": "How can I travel between San Francisco and Central Park by rail?",
        "expected": "route"
    },
    {
        "name": "Location spelling error",
        "question": "How do I get from San Fransisco to Central Park by train?",
        "expected": "route"
    },
    {
        "name": "Unknown route",
        "question": "How do I travel from Kuala Lumpur to Penang by train?",
        "expected": "no_records"
    },
    {
        "name": "Missing route details",
        "question": "When is the next train?",
        "expected": "no_records"
    },
    {
        "name": "Unavailable date",
        "question": "What time is the train from San Francisco to Central Park on 2099-12-31?",
        "expected": "no_records"
    },
    {
        "name": "General travel question",
        "question": "What are the best places to visit in Japan?",
        "expected": "general"
    },
    {
        "name": "Food recommendation",
        "question": "What food should I try in Los Angeles?",
        "expected": "general"
    },
    {
        "name": "Travel itinerary",
        "question": "Plan a 3-day itinerary in San Francisco.",
        "expected": "general"
    },
    {
        "name": "Single slang matching",
        "question": "This destination is dank.",
        "expected": "slang",
        "keywords": {"dank"}
    },
    {
        "name": "Multi-word slang matching",
        "question": "This beach hits different.",
        "expected": "slang",
        "keywords": {"hits different"}
    },
    {
        "name": "Multiple slang matching",
        "question": "Low key this place is G.O.A.T",
        "expected": "slang",
        "keywords": {"low key", "g.o.a.t"}
    },
    {
        "name": "Overlapping slang prevention",
        "question": "L+ratio",
        "expected": "slang",
        "keywords": {"l+ratio"}
    },
    {
        "name": "Normal question without slang",
        "question": "What are the tourist attractions in Japan?",
        "expected": "slang",
        "keywords": set()
    }
]

passed = 0
failed = 0

print("=" * 60)
print("STAGE 5.10 - AUTOMATED CHATBOT TESTING")
print("=" * 60)

for index, test in enumerate(tests, start=1):

    question = test["question"]

    try:
        travel = retrieve_travel_records(question)
        slang = retrieve_slang_records(question)
        transport = is_transport_question(question)

        keywords = {
            str(row["keyword"]).lower().strip()
            for row in slang
        }

        expected = test["expected"]

        if expected == "route":
            success = (
                transport
                and len(travel) > 0
                and all(
                    str(row["intent"]).lower() == "route_query"
                    and "san francisco" in str(row["entities"]).lower()
                    and "central park" in str(row["entities"]).lower()
                    and "train" in str(row["entities"]).lower()
                    for row in travel
                )
            )

        elif expected == "no_records":
            success = transport and len(travel) == 0

        elif expected == "general":
            success = not transport and len(travel) == 0

        elif expected == "slang":
            success = keywords == test["keywords"]

        else:
            success = False

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"\nTest {index}: {test['name']}")
        print(f"Question: {question}")
        print(f"Transport related: {transport}")
        print(f"Travel records: {len(travel)}")
        print(f"Detected slang: {sorted(keywords)}")
        print(f"Result: {status}")

    except Exception as e:
        failed += 1
        print(f"\nTest {index}: {test['name']}")
        print(f"Result: ERROR - {e}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Total tests : {len(tests)}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Success rate: {passed / len(tests) * 100:.2f}%")
print("=" * 60)
