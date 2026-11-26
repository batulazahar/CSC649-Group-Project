import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

from src.data_loader import load_travel_dataset, load_slang_dataset

from src.currency_converter import (
    convert_currency,
    parse_currency_question
)

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
        "what time", "when is", "next",
        "departure", "depart", "schedule",
        "timetable"
    ]):
        detected_intent = "schedule_query"

    elif any(phrase in question for phrase in [
        "how do i get", "how to get",
        "how can i travel", "how do i travel",
        "best way to travel", "best way to get",
        "way to travel", "way to get",
        "directions", "route", "travel from",
        "how long", "how much time",
        "how many minutes", "how many hours",
        "journey duration", "travel time",
        "trip duration", "time taken",
        "reach"
    ]) or (
        re.search(r"\bfrom\b.+\bto\b", question)
        or re.search(
            r"\b[a-z]+\s+to\s+[a-z]+.*\b(train|bus|metro)\b",
            question
        )
    ):
        detected_intent = "route_query"

    else:
        detected_intent = None


    
    
    # Step 2: Extract origin and destination

    origin = ""
    destination = ""

    # Pattern 1: From Brooklyn to Downtown
    route_match = re.search(
        r"from\s+(.+?)\s+to\s+(.+?)(?=\s+(?:using|by|running|operating|available|cancelled|canceled|delayed|today|tomorrow|next|this|on)\b|[?.!,]|$)",
        question
    )

    if route_match:

        origin = route_match.group(1).strip()
        destination = route_match.group(2).strip()

    else:

        # Pattern 2: Reach Downtown from Brooklyn
        route_match = re.search(
            r"reach\s+(.+?)\s+from\s+(.+?)(?=[?.!,]|$)",
            question
        )

        if route_match:

            destination = route_match.group(1).strip()
            origin = route_match.group(2).strip()

        else:

            # Pattern 3: Brooklyn to Downtown by bus
            route_match = re.search(
                r"^(.+?)\s+to\s+(.+?)(?=\s+(?:using|by|running|operating|available|today|tomorrow|next|this|on)\b|[?.!,]|$)",
                question
            )

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
            r"[^a-z0-9]+",
            " ",
            str(text).lower()
        ).strip()

    normalized_question = normalize_text(user_question)

    slang_aliases = {
        "cap": ["no cap"],
        "main character": ["main character energy"]
    }

    matched_slang = []

    for _, row in slang_df.iterrows():

        keyword = normalize_text(row["keyword"])

        search_terms = [keyword]

        if keyword in slang_aliases:
            search_terms.extend(slang_aliases[keyword])

        for term in search_terms:

            pattern = rf"\b{re.escape(term)}\b"

            if re.search(pattern, normalized_question):

                matched_slang.append(row)
                break

    return matched_slang


# ==========================================
# 6. GENERATE CHATBOT RESPONSE
# ==========================================

def get_chatbot_response(user_question):

    # Check whether the question is a currency conversion request
    currency_request = parse_currency_question(user_question)

    # Detect incomplete currency conversion questions
    currency_keywords = [
        "convert",
        "currency",
        "exchange rate",
        "how much",
        "worth",
        "change"
    ]

        # Detect unsupported three-letter currency codes
    if not currency_request and re.search(
        r"\b(?:convert|exchange)\b.*\b[A-Z]{3}\b.*\b(?:to|into)\b.*\b[A-Z]{3}\b",
        user_question,
        re.IGNORECASE
    ):

        return (
            "Sorry, I couldn't recognise one or both of the "
            "currency codes. Please check the currency codes "
            "and try again.\n\n"
            "For example: Convert 100 USD to MYR."
        )

    if not currency_request and any(
        keyword in user_question.lower()
        for keyword in currency_keywords
    ):

        if re.search(r"\d", user_question):

            return (
                "Sure! I can help you convert currencies. "
                "Please specify both the original currency "
                "and the target currency.\n\n"
                "For example: Convert 100 USD to MYR."
            )

    if currency_request:

        try:
            result = convert_currency(
                currency_request["amount"],
                currency_request["from_currency"],
                currency_request["to_currency"]
            )

            return (
                f"{result['amount']:,.2f} "
                f"{result['from_currency']} is equal to "
                f"{result['converted_amount']:,.2f} "
                f"{result['to_currency']}.\n"
                f"Exchange rate: 1 {result['from_currency']} = "
                f"{result['exchange_rate']} {result['to_currency']}.\n"
                f"Rate date: {result['rate_date'] or 'Same currency'}.\n\n"
                f"Note: This is a reference exchange rate, "
                f"not necessarily the rate offered by banks or money changers."
            )

        except (ValueError, ConnectionError) as error:
            return f"Sorry, I couldn't complete the currency conversion. {error}"

    # 1. Retrieve relevant information
    relevant_travel = retrieve_travel_records(user_question)
    relevant_slang = retrieve_slang_records(user_question)

    # 2. Prepare slang information
    slang_context = ""

    for row in relevant_slang:
        slang_context += (
            f"{row['keyword']}: {row['description']}\n"
        )

    question = user_question.lower()

    # 3. Identify transport-related questions
    transport_related = any(phrase in question for phrase in [
        "how do i get",
        "how to get",
        "directions",
        "route",
        "travel from",
        "train",
        "bus",
        "metro",
        "timetable",
        "schedule",
        "departure",
        "running",
        "operating",
        "delayed",
        "cancelled",
        "canceled"
    ])

    
    # 4. Handle direct slang questions using the dataset
    slang_question = any(phrase in question for phrase in [
        "what does",
        "what is",
        "what's",
        "meaning",
        "define",
        "explain"
    ])

    if relevant_slang and slang_question and not transport_related:

        slang_answers = []

        for row in relevant_slang:

            slang_answers.append(
                f"{row['keyword']}: {row['description']}"
            )

        return "\n\n".join(slang_answers)


    # 5. Decide which information source to use

    if not relevant_travel:

        # Transport question without matching dataset records
        if transport_related:
            return (
                "Sorry, I couldn't find matching transport "
                "information in our dataset. "
                "Please try another route or question."
            )

        # Detect unknown slang definition questions
        unknown_slang_question = bool(re.search(
            r"\bwhat does\b.*\bmean\b"
            r"|\bmeaning of\b"
            r"|\bdefine\b",
            question
        ))

        if unknown_slang_question:

            # Gemini handles slang that is not available in the CSV
            prompt = f"""
            You are a friendly Gen Z slang assistant.

            Explain the meaning of the slang word or phrase
            in the user's question.

            USER QUESTION:
            {user_question}

            INSTRUCTIONS:
            1. Explain the slang meaning clearly and accurately.
            2. Use simple and easy-to-understand language.
            3. Include one short example sentence.
            4. Keep the response concise (2-4 sentences).
            5. Do not provide travel recommendations or travel advice.
            6. Do not discuss unrelated topics.
            """

        else:

            # General travel question: use Gemini knowledge
            prompt = f"""
            You are a friendly and helpful Travel Chatbot.

            Answer the user's general travel question using
            your general knowledge.

            You can help with:
            - Tourist attractions
            - Travel destinations
            - Food recommendations
            - Travel itineraries
            - Travel tips
            - Travel activities

            GEN Z SLANG INFORMATION:
            {slang_context}

            USER QUESTION:
            {user_question}

            INSTRUCTIONS:
            1. Give useful and relevant travel information.
            2. Keep answers friendly and easy to understand.
            3. Do not invent real-time information.
            4. Do not invent transport schedules or service status.
            5. Tell users to verify information that may change.
            6. Explain slang expressions when relevant.
            """



    else:

        # 5. Dataset-based transport answers
        travel_context = ""

        route_match = re.search(
            r"from\s+(.+?)\s+to\s+(.+?)(?=\s+(?:using|by|running|operating|available|cancelled|canceled|delayed|today|tomorrow|next|this|on)\b|[?.!,]|$)",
            question
        )

        origin = ""
        destination = ""

        if route_match:
            origin = route_match.group(1).strip()
            destination = route_match.group(2).strip()

        exact_route_records = []

        for row in relevant_travel:

            record_query = str(row["query"]).lower()

            exact_route = False

            if origin and destination:
                exact_route = (
                    re.search(
                        rf"\bfrom\s+{re.escape(origin)}\s+to\s+{re.escape(destination)}\b",
                        record_query
                    ) is not None
                )

            if origin and destination:
                match_type = (
                    "EXACT ROUTE MATCH"
                    if exact_route
                    else "SIMILAR ROUTE - NOT AN EXACT MATCH"
                )

            if exact_route:
                exact_route_records.append(row)

            else:
                match_type = "RELEVANT RETRIEVED RECORD"

            travel_context += (
                f"Match Type: {match_type}\n"
                f"Question: {row['query']}\n"
                f"Intent: {row['intent']}\n"
                f"Entities: {row['entities']}\n"
                f"Answer: {row['response']}\n\n"
            )

                    
        # Check whether exact route records contain conflicting durations
        if exact_route_records:

            durations_by_mode = {}

            for row in exact_route_records:

                record_query = str(row["query"]).lower()
                record_response = str(row["response"]).lower()

                # Identify the transport mode
                mode = next(
                    (
                        transport for transport in ["train", "bus", "metro"]
                        if re.search(rf"\b{transport}\b", record_query)
                    ),
                    None
                )

                if not mode:
                    continue

                if mode not in durations_by_mode:
                    durations_by_mode[mode] = set()

                # Detect duration ranges, such as 38 to 61 minutes
                duration_ranges = re.findall(
                    r"(\d+(?:\.\d+)?)\s*(?:to|-)\s*"
                    r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?)",
                    record_response
                )

                for first_value, second_value, unit in duration_ranges:

                    multiplier = 60 if unit.startswith(("hour", "hr")) else 1

                    durations_by_mode[mode].add(
                        float(first_value) * multiplier
                    )

                    durations_by_mode[mode].add(
                        float(second_value) * multiplier
                    )

                # Detect individual durations, such as 38 minutes
                individual_durations = re.findall(
                    r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?)",
                    record_response
                )

                for value, unit in individual_durations:

                    multiplier = 60 if unit.startswith(("hour", "hr")) else 1

                    durations_by_mode[mode].add(
                        float(value) * multiplier
                    )

            # Check for conflicting durations within the same transport mode
            conflicting_durations = {
                mode: sorted(durations)
                for mode, durations in durations_by_mode.items()
                if len(durations) > 1
            }

            if conflicting_durations:

                conflict_messages = []

                for mode, durations in conflicting_durations.items():

                    duration_text = " and ".join(
                        f"{value:g} minutes"
                        for value in durations
                    )

                    conflict_messages.append(
                        f"{mode.title()}: {duration_text}"
                    )

                return (
                    f"Based on the available dataset, the journey "
                    f"from {origin.title()} to {destination.title()} "
                    f"contains conflicting duration information.\n\n"
                    f"{chr(10).join(conflict_messages)}\n\n"
                    f"Please verify the actual travel time with "
                    f"the transport provider."
                )


        prompt = f"""
        You are a helpful Travel Chatbot.

        Answer using ONLY the retrieved travel information
        for transport-related facts.

        TRAVEL INFORMATION:
        {travel_context}

        GEN Z SLANG INFORMATION:
        {slang_context}

        USER QUESTION:
        {user_question}

        INSTRUCTIONS:

        1. Answer clearly and naturally.
        2. Use retrieved records as your source for transport facts.
        3. Exact route matches may be used for route-specific answers.
        4. Similar routes must NEVER be treated as exact routes.
        5. If the requested route is unavailable, explain this.
        6. Never invent schedules, prices, routes, journey durations
           or service status.
        7. If information is missing, state that it is unavailable.
        8. Explain slang expressions when relevant.
        9. If records conflict, explain that verification is needed.
        10. Keep the response concise and easy to understand.

        IMPORTANT RULES:
        - Never invent travel conditions, reasons, or explanations
          that are not explicitly stated in the retrieved records.
        - Do not assume travel durations depend on morning,
          afternoon, evening, or night unless the dataset says so.
        - If multiple records provide different durations for the
          same route, clearly report both durations.
        - Explain that the retrieved records contain inconsistent
          travel information.
        - Do not create a reason to explain conflicting information.
        """

    # 6. Generate response using Gemini
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
