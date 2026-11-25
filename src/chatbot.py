
import os
from dotenv import load_dotenv
from google import genai
from dotenv import load_dotenv

from data_loader import load_travel_dataset, load_slang_dataset

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

# Initialize Gemini
client = genai.Client(api_key=API_KEY)

# Load both datasets using data_loader.py
travel_df = load_travel_dataset()
slang_df = load_slang_dataset()


import re


def retrieve_travel_records(user_question, top_n=5):
    question = user_question.lower()

    # Identify the origin and destination
    route_match = re.search(
        r"from\s+(.+?)\s+to\s+(.+?)(?:\s+using\s+|\?|$)",
        question
    )

    origin = ""
    destination = ""

    if route_match:
        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()

    stop_words = {
        "how", "what", "where", "when", "why", "who",
        "do", "does", "is", "are", "can", "could",
        "i", "you", "we", "the", "a", "an", "to",
        "from", "in", "on", "at", "for", "of", "and",
        "me", "my", "please", "there", "get", "using"
    }

    question_words = set(
        re.findall(r"\b\w+\b", question)
    ) - stop_words

    scored_records = []

    for _, row in travel_df.iterrows():
        record_query = str(row["query"]).lower()

        record_words = set(
            re.findall(r"\b\w+\b", record_query)
        )

        score = len(question_words.intersection(record_words))

        # Give higher priority to the exact route direction
        
        if origin and destination:
            # Keep only records with the exact route direction
            if f"from {origin} to {destination}" not in record_query:
                continue

            score += 20

            # Match the requested transport type
            transport_modes = ["train", "bus", "metro"]

            requested_mode = next(
                (mode for mode in transport_modes if mode in question_words),
                None
            )

            if requested_mode:
                if requested_mode not in record_query:
                    continue

                score += 10


        if score > 0:
            scored_records.append((score, row))

    scored_records.sort(key=lambda item: item[0], reverse=True)

    return [row for score, row in scored_records[:top_n]]



def retrieve_slang_records(user_question):
    def normalize_text(text):
        return re.sub(r"[^a-z0-9]", "", str(text).lower())

    question_words = re.findall(r"[a-z0-9]+", user_question.lower())

    matched_slang = []

    for _, row in slang_df.iterrows():
        keyword = str(row["keyword"]).strip()

        normalized_keyword = normalize_text(keyword)

        for word in question_words:
            if normalize_text(word) == normalized_keyword:
                matched_slang.append(row)
                break

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
        model="gemini-3.8-flash",
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
