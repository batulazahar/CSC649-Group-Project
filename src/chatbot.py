
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

from src.data_loader import load_travel_dataset, load_slang_dataset


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )


# ==========================================
# 2. INITIALIZE GEMINI
# ==========================================

client = genai.Client(api_key=API_KEY)


# ==========================================
# 3. LOAD DATASETS
# ==========================================

travel_df = load_travel_dataset()
slang_df = load_slang_dataset()


# ==========================================
# 4. TRAVEL DATA RETRIEVAL
# ==========================================




def retrieve_travel_records(user_question, top_n=5):

    question = user_question.lower()

    # Step 1: Detect the user's intent
    if any(phrase in question for phrase in [
        "running", "operating", "service status",
        "cancelled", "canceled", "delayed",
        "service interruption", "available",
        "availability", "is there a train",
        "is there a bus", "is there a metro",
        "train service", "bus service", "metro service"
    ]):
        detected_intent = "status_query"

    
    elif any(phrase in question for phrase in [
        "how do i get", "how to get", "directions",
        "route", "way to", "travel from",
        "how long", "how much time",
        "how many minutes", "how many hours",
        "journey duration", "travel time",
        "trip duration"
    ]):
        detected_intent = "route_query"


    elif any(phrase in question for phrase in [
        "what time", "when is", "next", "departure",
        "depart", "schedule", "timetable"
    ]):
        detected_intent = "schedule_query"

    else:
        detected_intent = None

    # Step 2: Extract origin and destination
    route_match = re.search(
        r"from\s+(.+?)\s+to\s+(.+?)(?=\s+(?:using|by|running|operating|available|cancelled|canceled|delayed|today|tomorrow|next|this|on)\b|[?.!,]|$)",
        question
    )

    origin = ""
    destination = ""

    if route_match:
        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()

    # Step 3: Identify transport mode
    transport_modes = ["train", "bus", "metro"]

    requested_mode = next(
        (
            mode for mode in transport_modes
            if re.search(rf"\b{mode}\b", question)
        ),
        None
    )

    # Step 4: Prepare keywords for similarity matching
    stop_words = {
        "how", "what", "where", "when", "why", "who",
        "do", "does", "is", "are", "can", "could",
        "will", "has", "have", "been",
        "i", "you", "we", "the", "a", "an", "to",
        "from", "in", "on", "at", "for", "of", "and",
        "me", "my", "please", "there", "get", "using",
        "time", "next", "this", "that", "be"
    }

    question_words = set(
        re.findall(r"\b\w+\b", question)
    ) - stop_words

    exact_matches = []
    similar_matches = []

    seen_records = set()

    # Step 5: Retrieve and rank records
    for _, row in travel_df.iterrows():

        record_query = " ".join(str(row["query"]).lower().split())
        record_intent = str(row["intent"]).lower()

        # Filter by intent
        if detected_intent and record_intent != detected_intent:
            continue

        # Filter by transport mode
        if requested_mode and not re.search(
            rf"\b{requested_mode}\b", record_query
        ):
            continue

        # Remove duplicate records
        
        # Remove only completely identical records
        record_key = (
            record_query,
            record_intent,
            " ".join(str(row["entities"]).lower().split()),
            " ".join(str(row["response"]).lower().split())
        )

        if record_key in seen_records:
            continue

        seen_records.add(record_key)

        record_words = set(
            re.findall(r"\b\w+\b", record_query)
        )

        score = len(
            question_words.intersection(record_words)
        )

        if score == 0:
            continue

        # Check exact origin and destination
        exact_route = False

        if origin and destination:

            exact_route = (
                re.search(
                    rf"\bfrom\s+{re.escape(origin)}\s+to\s+{re.escape(destination)}\b",
                    record_query
                ) is not None
            )

        if exact_route:

            score += 30
            exact_matches.append((score, row))

        else:

            similar_matches.append((score, row))

    # Step 6: Sort records by relevance
    exact_matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    similar_matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # Step 7: Prioritise exact routes
    if exact_matches:

        return [
            row for score, row in exact_matches[:top_n]
        ]

    # Use similar records only if exact routes are unavailable
    return [
        row for score, row in similar_matches[:top_n]
    ]



# ==========================================
# 5. SLANG DATA RETRIEVAL
# ==========================================

def retrieve_slang_records(user_question):

    def normalize_text(text):
        return re.sub(
            r"[^a-z0-9]",
            "",
            str(text).lower()
        )

    question_words = re.findall(
        r"[a-z0-9]+",
        user_question.lower()
    )

    matched_slang = []

    for _, row in slang_df.iterrows():

        keyword = str(row["keyword"]).strip()

        normalized_keyword = normalize_text(keyword)

        for word in question_words:

            if normalize_text(word) == normalized_keyword:
                matched_slang.append(row)
                break

    return matched_slang


# ==========================================
# 6. GENERATE CHATBOT RESPONSE
# ==========================================


def get_chatbot_response(user_question):

    # Retrieve relevant travel records
    relevant_travel = retrieve_travel_records(user_question)

    # Retrieve relevant slang records
    relevant_slang = retrieve_slang_records(user_question)

    # Check whether travel records are available
    if not relevant_travel:

        if relevant_slang:

            slang_answers = []

            for row in relevant_slang:

                slang_answers.append(
                    f"{row['keyword']}: {row['description']}"
                )

            return (
                "Here are the slang meanings:\n"
                + "\n".join(slang_answers)
            )

        return (
            "Sorry, I couldn't find relevant information "
            "in the travel dataset. Please try another question."
        )

    # Extract the requested route
    route_match = re.search(
        r"from\s+(.+?)\s+to\s+(.+?)(?=\s+(?:using|by|running|operating|available|cancelled|canceled|delayed|today|tomorrow|next|this|on)\b|[?.!,]|$)",
        user_question.lower()
    )

    origin = ""
    destination = ""

    if route_match:

        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()

    # Prepare travel information
    travel_context = ""

    for row in relevant_travel:

        record_query = str(row["query"]).lower()

        # Determine whether the retrieved route is exact
        exact_route = False

        if origin and destination:

            exact_route = (
                re.search(
                    rf"\bfrom\s+{re.escape(origin)}\s+to\s+{re.escape(destination)}\b",
                    record_query
                ) is not None
            )

        if origin and destination:

            if exact_route:
                match_type = "EXACT ROUTE MATCH"

            else:
                match_type = "SIMILAR ROUTE - NOT AN EXACT MATCH"

        else:

            match_type = "RELEVANT RETRIEVED RECORD"

        travel_context += (
            f"Match Type: {match_type}\n"
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

    Your answers MUST be based only on the retrieved
    information provided below.

    TRAVEL INFORMATION:
    {travel_context}

    GEN Z SLANG INFORMATION:
    {slang_context}

    USER QUESTION:
    {user_question}

    INSTRUCTIONS:

    1. Answer the user's question clearly and naturally.

    2. Use retrieved travel records as your source
       of information.

    3. Pay attention to the Match Type of each record.

    4. EXACT ROUTE MATCH records may be used to answer
       route-specific questions.

    5. SIMILAR ROUTE records are only references.
       NEVER use their journey duration, destination,
       departure time or other details as the answer
       for a different requested route.

    6. If no exact route information is available,
       clearly explain that the requested route
       information is unavailable.

    7. Use slang information to understand Gen Z
       expressions used by the user.

    8. Do not add information that is not supported
       by the retrieved records.

    9. Never assume that a transport service is
       operating normally or currently available.

    10. If schedules, service status or booking details
        are not provided in the retrieved records,
        clearly state that the information is unavailable.

    11. Do not invent transport schedules, prices,
        routes or service status.

    12. Preserve all factual details from the dataset,
        including transport modes, locations, times
        and journey durations.

    13. If the retrieved information does not answer
        the user's question, explain this clearly.

    14. Keep your response concise and easy to understand.
    
    15. If multiple retrieved records contain conflicting
        information for the same question or route,
        DO NOT choose one answer arbitrarily.

    16. Clearly explain that the dataset contains
        different answers for the same route.

    17. NEVER invent reasons for conflicting information.
        For example, do not assume that different journey
        durations are caused by different times of day,
        traffic conditions or transport services unless
        the retrieved records explicitly state this.

    18. If conflicting information exists, present the
        different values exactly as provided and explain
        that the information needs verification.

    """

    # Generate response using Gemini
    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return (
                response.text
                or "Sorry, I couldn't generate a response."
            )

        except APIError as e:

            if e.code == 503:

                if attempt < 2:

                    print(
                        f"Gemini is busy. Retrying... "
                        f"({attempt + 1}/3)"
                    )

                    time.sleep(2 ** (attempt + 1))

                else:

                    return (
                        "Gemini is currently unavailable. "
                        "Please try again later."
                    )

            else:

                return f"Gemini API error ({e.code}): {e}"

        except Exception as e:

            return f"An unexpected error occurred: {e}"
        
# ==========================================
# 7. RUN CHATBOT IN TERMINAL
# ==========================================

if __name__ == "__main__":

    print("Travel Chatbot is ready!")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":

            print("Chatbot: Goodbye!")
            break

        # Check retrieved travel records
        records = retrieve_travel_records(question)

        print("\n--- RETRIEVED TRAVEL RECORDS ---")

        if records:

            for row in records:

                print("Question:", row["query"])
                print("Intent:", row["intent"])
                print("Response:", row["response"])
                print("------------------------------")

        else:

            print("No relevant travel records found.")

        # Generate chatbot response
        answer = get_chatbot_response(question)

        print("\nChatbot:", answer)
        print()
