
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


def get_chatbot_response(user_question):

    # Prepare travel dataset information
    travel_context = ""

    for _, row in travel_df.iterrows():
        travel_context += (
            f"Question: {row['query']}\n"
            f"Intent: {row['intent']}\n"
            f"Entities: {row['entities']}\n"
            f"Answer: {row['response']}\n\n"
        )

    # Prepare Gen Z slang information
    slang_context = ""

    for _, row in slang_df.iterrows():
        slang_context += (
            f"Slang: {row['keyword']}\n"
            f"Meaning: {row['description']}\n\n"
        )

    # Create prompt
    prompt = f"""
    You are a helpful Travel Chatbot.

    Use the travel dataset as your main source
    of travel information.

    Use the Gen Z slang dataset to understand
    slang words used by users.

    TRAVEL DATASET:
    {travel_context}

    GEN Z SLANG DATASET:
    {slang_context}

    USER QUESTION:
    {user_question}

    INSTRUCTIONS:
    1. Answer travel-related questions clearly.
    2. Understand Gen Z slang using the slang dataset.
    3. Use both datasets when relevant.
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
