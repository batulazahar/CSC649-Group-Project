
from src.chatbot import (
    retrieve_travel_records,
    retrieve_slang_records,
    get_chatbot_response
)


# TC01: Test travel information retrieval
def test_travel_retrieval():
    question = "How do I get from San Francisco to Central Park using train?"

    records = retrieve_travel_records(question)

    assert records is not None
    assert len(records) > 0


# TC02: Test Gen Z slang retrieval
def test_slang_retrieval():
    question = "What does G.O.A.T. mean?"

    records = retrieve_slang_records(question)

    assert records is not None
    assert len(records) > 0


# TC03: Test chatbot response generation
def test_chatbot_response():
    question = "How do I get from San Francisco to Central Park using train?"

    answer = get_chatbot_response(question)

    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0
