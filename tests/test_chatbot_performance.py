
import time
import statistics
import csv
from src.chatbot import get_chatbot_response


# Number of times each question will be tested
TEST_RUNS = 5


# Questions from different chatbot categories
test_questions = {
    "Travel Route": "How do I get from Brooklyn to Downtown?",
    "Travel Status": "Is the train from Brooklyn to Downtown running next Monday?",
    "Currency Conversion": "Convert 100 USD to MYR",
    "Gen Z Slang": "What does cheugy mean?",
    "General Travel": "What are the best places to visit in Paris?"
}


# Store performance results
performance_results = {}


# Run performance tests
for category, question in test_questions.items():

    print("\n" + "=" * 60)
    print("Category:", category)
    print("Question:", question)
    print("=" * 60)

    response_times = []

    for run in range(TEST_RUNS):

        start_time = time.perf_counter()
        response = get_chatbot_response(question)
        end_time = time.perf_counter()

        response_time = end_time - start_time
        response_times.append(response_time)

        print(f"Run {run + 1}: {response_time:.4f} seconds")

    average_time = statistics.mean(response_times)
    minimum_time = min(response_times)
    maximum_time = max(response_times)

    performance_results[category] = {
        "average": average_time,
        "minimum": minimum_time,
        "maximum": maximum_time
    }

    print("\nAverage Response Time:", round(average_time, 4), "seconds")
    print("Fastest Response Time:", round(minimum_time, 4), "seconds")
    print("Slowest Response Time:", round(maximum_time, 4), "seconds")


# Display final performance summary
print("\n\n")
print("=" * 75)
print("CHATBOT RESPONSE TIME PERFORMANCE SUMMARY")
print("=" * 75)

for category, results in performance_results.items():

    print("\nCategory:", category)
    print("Average:", round(results["average"], 4), "seconds")
    print("Minimum:", round(results["minimum"], 4), "seconds")
    print("Maximum:", round(results["maximum"], 4), "seconds")


# Export performance results to CSV
with open("performance_results.csv", "w", newline="", encoding="utf-8") as csv_file:

    fieldnames = [
        "Category",
        "Average Response Time (seconds)",
        "Fastest Response Time (seconds)",
        "Slowest Response Time (seconds)"
    ]

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for category, results in performance_results.items():

        writer.writerow({
            "Category": category,
            "Average Response Time (seconds)": round(results["average"], 4),
            "Fastest Response Time (seconds)": round(results["minimum"], 4),
            "Slowest Response Time (seconds)": round(results["maximum"], 4)
        })


print("\nPerformance results saved to performance_results.csv")
print("Performance testing completed!")
