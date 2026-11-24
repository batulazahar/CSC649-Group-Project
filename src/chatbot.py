
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

# Initialize Gemini
client = genai.Client(api_key=API_KEY)

# Dataset paths
TRAVEL_DATASET_PATH = "data/TransitChat-Conversational_Route_and_Schedule_Dataset (1).csv"
SLANG_DATASET_PATH = "data/genz_slang.csv"

# Load both datasets
travel_df = pd.read_csv(TRAVEL_DATASET_PATH)
slang_df = pd.read_csv(SLANG_DATASET_PATH)


import re

def retrieve_travel_records(user_question, top_n=5):
    stop_words = {
        "how", "what", "where", "when", "why", "who",
        "do", "does", "is", "are", "can", "could",
        "i", "you", "we", "the", "a", "an", "to",
        "from", "in", "on", "at", "for", "of", "and",
        "me", "my", "please", "there", "get"
    }

    question_words = set(
        re.findall(r"\b\w+\b", user_question.lower())
    ) - stop_words

    scored_records = []

    for _, row in travel_df.iterrows():
        record_text = " ".join([
            str(row["query"]),
            str(row["intent"]),
            str(row["entities"]),
            str(row["response"])
        ]).lower()

        record_words = set(
            re.findall(r"\b\w+\b", record_text)
        )

        score = len(question_words.intersection(record_words))

        if score > 0:
            scored_records.append((score, row))

    scored_records.sort(key=lambda item: item[0], reverse=True)

    return [row for score, row in scored_records[:top_n]]


def retrieve_slang_records(user_question):
    question_words = set(
        re.findall(r"\b\w+\b", user_question.lower())
    )

    matched_slang = []

    for _, row in slang_df.iterrows():
        keyword = str(row["keyword"]).lower()

        # Check whether the slang appears in the question
        if keyword in user_question.lower():
            matched_slang.append(row)

    return matched_slang



def get_chatbot_response(user_question):

    # Retrieve relevant travel records
    relevant_travel = retrieve_travel_records(user_question)

    # Retrieve relevant slang records
    relevant_slang = retrieve_slang_records(user_question)

    # Prepare travel information
    travel_context = ""

    for row in relevant_travel:
        travel_context += (
            f"Question: {row['query']}\n"
            f"Intent: {row['intent']}\n"
            f"Entities: {row['entities']}\n"
            f"Answer: {row['response']}\n\n"
        )

    # Prepare slang information
    slang_context = ""

    for row in relevant_slang:
        slang_context += (
            f"Slang: {row['keyword']}\n"
            f"Meaning: {row['description']}\n\n"
        )

    # Create prompt
    prompt = f"""
    You are a helpful Travel Chatbot.

    Use the retrieved travel records as your main source
    of travel information.

    Use the retrieved slang records to understand
    slang words used by users.

    TRAVEL INFORMATION:
    {travel_context}

    GEN Z SLANG INFORMATION:
    {slang_context}

    USER QUESTION:
    {user_question}

    INSTRUCTIONS:
    1. Answer travel-related questions clearly.
    2. Understand Gen Z slang using the slang information.
    3. Use the retrieved information when relevant.
    4. Do not invent transport schedules or service status.
    5. If the required travel information is unavailable,
       explain that it is not available in the dataset.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text



# Run chatbot
if __name__ == "__main__":

    print("Travel Chatbot is ready!")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ")

        if question.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        answer = get_chatbot_response(question)

        print("\nChatbot:", answer)
        print()
