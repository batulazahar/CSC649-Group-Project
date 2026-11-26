# Travel Chatbot – System Test Cases

## 1. Introduction

This document describes the system test cases for the Travel Chatbot. The testing is conducted to verify the functionality of the chatbot, including travel information retrieval, Gen Z slang detection, response generation, invalid input handling, and frontend-backend integration.

## 2. Test Environment

- Programming Language: Python
- Backend Framework: Flask
- AI Model/API: Google Gemini API
- Dataset: Travel Dataset and Gen Z Slang Dataset
- Frontend: HTML, CSS and JavaScript
- Testing Environment: Localhost

## 3. Test Cases

| Test ID | Test Area | Test Description | Test Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| TC01 | Travel Query | Test travel information retrieval | How do I get from San Francisco to Central Park using train? | Chatbot provides relevant travel information from the dataset. | Chatbot returned the correct train route information with an estimated journey time of 28 minutes. | Pass |
| TC02 | Travel Query | Test reverse travel direction | How do I get from Central Park to San Francisco using train? | Chatbot retrieves the correct travel information. | Chatbot returned the correct reverse train route information with an estimated journey time of 20 minutes. | Pass |
| TC03 | Gen Z Slang | Test slang detection | What does G.O.A.T. mean? | Chatbot explains the meaning of G.O.A.T. | Chatbot correctly explained that G.O.A.T. means "Greatest Of All Time" and provided additional examples. | Pass |
| TC04 | Gen Z Slang | Test another slang keyword | What does W mean in Gen Z slang? | Chatbot explains the meaning of W. | Chatbot correctly explained that "W" means "Win" in Gen Z slang and provided relevant examples. | Pass |
| TC05 | Response Generation | Test chatbot response relevance | How do I get from San Francisco to Central Park using train? | Chatbot generates a relevant and understandable response. | Chatbot generated a clear and relevant response with the correct train route and estimated journey time of 28 minutes. | Pass |
| TC06 | Invalid Input | Test empty message handling | Empty message | System prevents empty messages from being submitted. | No message or chatbot response appeared when the Send button was clicked with an empty input. | Pass |
| TC07 | Frontend Functionality | Test message submission | Hello, how are you? | User message and chatbot response appear in the chat interface. | The user's message and chatbot response were successfully displayed in the chat interface. | Pass |
| TC08 | Backend Integration | Test communication with Flask API | How do I get from San Francisco to Central Park using train? | Flask processes the request and returns a chatbot response. | The Flask `/chat` endpoint successfully processed the POST request and returned a chatbot response in JSON format. | Pass |

## 4. Testing Results

A total of eight (8) test cases were conducted to evaluate the Travel Chatbot system.

All eight test cases passed, covering travel information retrieval, Gen Z slang detection, response generation, empty input handling, frontend functionality, and backend integration.

However, during the empty input test, the system prevented the submission of an empty message but did not display a warning or validation message to the user. This can be considered an area for future improvement.

## 5. Conclusion

The system testing results indicate that the Travel Chatbot successfully performs its main functions. The chatbot was able to retrieve travel information, identify Gen Z slang, generate relevant responses, and communicate successfully with the Flask backend through the frontend interface.

Overall, the testing demonstrates that the core functionality and frontend-backend integration of the Travel Chatbot are working as expected.