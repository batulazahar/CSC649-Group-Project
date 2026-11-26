\# Source Code (src)



This folder contains the backend modules responsible for the chatbot's core functionality, dataset processing, AI integration and currency conversion.



\## 1. chatbot.py



The main chatbot module that processes user questions and generates responses.



Main responsibilities:

\- Identifies user intents and processes travel-related enquiries.

\- Retrieves relevant information from the travel and Gen Z slang datasets.

\- Integrates Google Gemini API for AI-powered response generation.

\- Handles general travel questions and unsupported dataset queries.

\- Connects the chatbot with the currency conversion module.



\## 2. data\_loader.py



Responsible for loading the CSV datasets using pandas.



Main responsibilities:

\- Loads `travel\_dataset\_verified.csv`.

\- Loads `genz\_slang.csv`.

\- Checks whether dataset files exist and contain records.

\- Provides dataset loading functions for the chatbot module.



\## 3. currency\_converter.py



Handles currency conversion functionality using the Frankfurter API.



Main responsibilities:

\- Retrieves exchange-rate information from the Frankfurter API.

\- Converts an amount from one currency to another.

\- Identifies currency codes and aliases from user questions.

\- Handles API errors and connection issues.



\## 4. Technologies Used



\- Python

\- pandas

\- Google GenAI SDK

\- python-dotenv

\- Frankfurter API



\## 5. Environment Configuration



The chatbot requires a Google Gemini API key.



The API key is configured using the `GEMINI\_API\_KEY` environment variable in the project's root `.env` file.



Do not store API keys directly in the source code or commit the `.env` file to GitHub.

