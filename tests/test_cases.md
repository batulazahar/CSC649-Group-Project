

\# Automated Chatbot Testing – Test Cases



\## Testing Information



\- Project: TravelMate AI

\- GitHub Issue: #20 – Implement Automated Chatbot Testing

\- Test file: `tests/test\_chatbot.py`

\- Testing framework: pytest

\- Test result: 4 passed, 0 failed



\## Test Cases



| Test ID | Test Description | Test Input | Expected Result | Actual Result | Status |

|---|---|---|---|---|---|

| TC01 | Travel information retrieval | How do I get from San Francisco to Central Park using train? | Relevant travel records are retrieved. | Travel records were successfully retrieved. | PASSED |

| TC02 | Gen Z slang retrieval | What does G.O.A.T. mean? | Relevant slang records are retrieved. | G.O.A.T. was retrieved with its description. | PASSED |

| TC03 | Chatbot response generation | How do I get from San Francisco to Central Park using train? | Chatbot generates a non-empty text response. | Chatbot generated a response successfully. | PASSED |

| TC04 | Empty user input | Empty string (`""`) | Chatbot returns a message asking the user to provide a question. | Chatbot returned an empty-input guidance message. | PASSED |



\## Testing Execution



Command used:



```powershell

.\\.venv\\Scripts\\python.exe -m pytest tests/test\_chatbot.py -v

```



\## Testing Results



\- Total test cases: 4

\- Passed: 4

\- Failed: 0



\*\*Overall Result: PASSED\*\*



All four automated test cases passed successfully.



