# Testing

This folder contains testing resources for evaluating the chatbot's functionality and performance.

## 1. System Test Cases

The main system test cases are documented in the root `test_cases.md` file.

They cover:
- Travel information retrieval.
- Gen Z slang detection.
- Chatbot response generation.
- Empty input handling.
- Frontend and backend integration.

## 2. Performance Testing

**File:** `test_chatbot_performance.py`

This script measures the chatbot's response time across five categories:
- Travel Route
- Travel Status
- Currency Conversion
- Gen Z Slang
- General Travel

Each question is tested five times. The script calculates the average, minimum and maximum response times and exports the results to `performance_results.csv` in the project root.

### How to Run

```bash
python tests/test_chatbot_performance.py
```

## 3. Automated Chatbot Testing

**File:** `test_chatbot.py`

This file contains automated tests for:
- Travel information retrieval.
- Gen Z slang retrieval.
- Chatbot response generation.

### How to Run

```bash
python -m pytest tests/test_chatbot.py -v
```

### Test Results

The automated tests were executed successfully.

- Total test cases: 3
- Passed: 3
- Failed: 0

## 4. Additional Test Scripts

Other testing scripts are available in the project root:
- `test_chatbot_e2e.py`
- `test_chatbot_stage5.py`
- `test_gemini.py`

Some tests may require a valid Gemini API key and an active internet connection.