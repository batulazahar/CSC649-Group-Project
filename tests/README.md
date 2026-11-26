\# Testing



This folder contains testing resources for evaluating the chatbot's functionality and response-time performance.



\## 1. System Test Cases



The main system test cases are documented in the root `test\_cases.md` file.



They cover:

\- Travel information retrieval.

\- Gen Z slang detection.

\- Chatbot response generation.

\- Empty input handling.

\- Frontend and backend integration.



\## 2. Performance Testing



\*\*File:\*\* `test\_chatbot\_performance.py`



This script measures the chatbot's response time across five categories:



\- Travel Route

\- Travel Status

\- Currency Conversion

\- Gen Z Slang

\- General Travel



Each question is tested five times. The script calculates the average, minimum and maximum response times and exports the results to `performance\_results.csv` in the project root.



\### How to Run



Run this command from the project root directory:



```bash

python tests/test\_chatbot\_performance.py

```



\## 3. Additional Test Scripts



Other testing scripts are available in the project root:



\- `test\_chatbot\_e2e.py`

\- `test\_chatbot\_stage5.py`

\- `test\_gemini.py`



Some tests may require a valid Gemini API key and an active internet connection.

