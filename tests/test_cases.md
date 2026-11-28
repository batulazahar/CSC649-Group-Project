

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

## Manual Testing Results

| Test ID | Test Description | Test Input | Actual Result | Status |
|---|---|---|---|---|
| MT01 | Currency conversion | Currency conversion questions | Currency conversion completed successfully. | PASSED |
| MT02 | Known slang detection | What does G.O.A.T. mean? | Correct slang meaning retrieved. | PASSED |
| MT03 | Unknown slang handling | What does rizz mean? | Gemini provided a slang explanation. | PASSED |
| MT04 | Travel fallback | How do I travel from Kuala Lumpur to Penang using train? | Gemini provided general travel guidance. | PASSED |
| MT05 | Travel budget summary | Show my travel budget summary. (Budget RM1,000; expenses RM0) | System displayed the correct budget, expenses and remaining balance. | PASSED |
| MT06 | Budget warning at 80% | Record expenses totalling RM800 against RM1,000 budget. | System displayed an 80% budget usage warning. | PASSED |
| MT07 | Budget exceeded warning | Record an additional RM250 expense. | System displayed RM1,050 total expenses, RM-50 remaining balance and a budget exceeded warning. | PASSED |
| MT08 | Expense Tracker integration | Record RM800 for Food and RM250 for Transport. | Expenses were successfully recorded and included in the budget summary. | PASSED |


### Automated Testing
- Total test cases: 4
- Passed: 4
- Failed: 0

### Manual Testing
- Total test cases: 8
- Passed: 8
- Failed: 0

### Overall Testing
- Total test cases: 12
- Passed: 12
- Failed: 0

**Overall Result: PASSED**





