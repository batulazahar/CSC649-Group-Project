# Travel Budget Management Chatbot

A domain-specific chatbot designed to assist travellers with travel-related information, transportation enquiries, currency conversion and general travel questions using Google Gemini.

## 1. Project Overview

The Travel Budget Management Chatbot is a web-based chatbot developed to support travellers when preparing for and planning their trips.

Travellers may need assistance finding transportation information, checking travel schedules, understanding currency exchange rates and getting recommendations about destinations. This chatbot provides a single interface where users can ask travel-related questions and receive relevant responses.

The system combines a custom CSV dataset, a currency exchange API and a Large Language Model (LLM) to process user enquiries.

## 2. Problem Statement

Travellers may experience difficulties when searching for travel information from different sources. These difficulties include:

- Finding suitable transportation routes between destinations.
- Obtaining information about transportation schedules and service status.
- Understanding currency exchange rates when travelling overseas.
- Getting relevant answers to general travel questions.
- Understanding unfamiliar Gen Z slang used in online travel conversations.

The chatbot aims to make travel-related information easier to access through a conversational interface.

## 3. Project Objectives

1. To develop a web-based chatbot that provides travel-related information through natural language conversations.
2. To retrieve relevant transportation information from a custom travel dataset.
3. To integrate currency conversion functionality using an external exchange-rate API.
4. To provide general travel information and explanations using Google Gemini.
5. To provide explanations of Gen Z slang using a custom dataset and AI-generated responses where appropriate.

## 4. Main Functions

### 4.1 Travel Information Retrieval

Retrieves relevant information from the custom travel dataset to answer transportation-related questions, including routes, schedules and service-status enquiries.

### 4.2 Currency Conversion

Converts currencies using exchange-rate information from the Frankfurter API.

### 4.3 Gen Z Slang Explanation

Identifies Gen Z slang keywords from the custom slang dataset and provides their meanings. Gemini can also assist when a slang term is not available in the dataset.

### 4.4 General Travel Assistance

Uses Google Gemini to answer general travel questions, such as destination recommendations and travel-related suggestions.

### 4.5 Planned Enhancement: Travel Budget Allocation

A future enhancement will allow users to enter their travel destination and total budget. The chatbot will then recommend an estimated budget allocation across categories such as:

- Food and beverages
- Accommodation
- Transportation
- Shopping
- Activities and entertainment
- Emergency and miscellaneous expenses

This feature is planned for future development and is not yet part of the current implementation.

## 5. Team Members

| Name | GitHub Profile | Role |
|---|---|---|
| NUR IRDINA BATRISYA BINTI ZULHAZMI | [irdinazlhzm](https://github.com/irdinazlhzm) | Project Leader |
| NUR EMALLYN SOFEA BINTI NORIZAL | [emallynsofea](https://github.com/emallynsofea) | Backend Developer |
| NURBATUL ZAYNAB BINTI DARUL AZAHAR | [batulazahar](https://github.com/batulazahar) | Frontend Developer / Model Integrator |
| TIJANIE MARSYA BINTI ROSLIM | [janieroslim1230](https://github.com/janieroslim1230) | Frontend Developer / Domain Specialist |

## 6. Domain and Datasets

**Selected Domain:** Travel

The project uses custom CSV datasets to support travel information retrieval and Gen Z slang explanations.

| Dataset | Records | Description |
|---|---:|---|
| `travel_dataset_verified.csv` | 497 | Contains travel questions, intent labels, entities and corresponding responses. |
| `genz_slang.csv` | 145 | Contains Gen Z slang keywords and their descriptions. |

**Travel dataset columns:**
- `query`
- `intent`
- `entities`
- `response`

**Gen Z slang dataset columns:**
- `keyword`
- `description`

The datasets are stored in the `data/` directory and loaded by `src/data_loader.py`.

## 7. System Architecture

The system follows a client-server architecture that combines dataset retrieval, external API integration and AI-powered response generation.

### System Workflow

1. The user enters a question through the chatbot web interface.
2. The Flask backend receives the request through the `/chat` endpoint.
3. The chatbot processes the question and identifies the relevant intent.
4. Depending on the question, the system retrieves information from the travel or slang dataset, accesses the currency conversion API, or uses Gemini.
5. The chatbot generates a response.
6. The response is returned to the frontend and displayed to the user.


## 8. Technologies and Model

| Component | Technology | Purpose |
|---|---|---|
| Programming Language | Python | Backend development and chatbot logic |
| Frontend | HTML, CSS, JavaScript | Chatbot user interface |
| Backend Framework | Flask | Handles web requests and chatbot communication |
| AI Model | Gemini 3.5 Flash Lite | Generates AI-powered responses |
| AI Integration | Google GenAI SDK | Connects the application to Gemini |
| Data Processing | pandas | Loads and processes CSV datasets |
| Environment Configuration | python-dotenv | Loads API credentials from environment variables |
| Currency API | Frankfurter API | Retrieves currency exchange rates |

### Model Integration

The project integrates Google's Gemini model using the `google-genai` Python package.

**Model:** `gemini-3.5-flash-lite`

**Integration method:** The chatbot sends a prompt to the Gemini API using the Google GenAI SDK and processes the generated response.

The Gemini API key is stored in an environment variable named `GEMINI_API_KEY` to avoid exposing sensitive credentials in the source code.

## 9. Project Structure

```text
CSC649-Group-Project/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   ├── templates/
│   │   └── index.html
│   └── README.md
│
├── data/
│   ├── travel_dataset_verified.csv
│   ├── genz_slang.csv
│   ├── TransitChat-Conversational_Route_and_Schedule_Dataset (1).csv
│   └── README.md
│
├── docs/
│   └── README.md
│
├── src/
│   ├── chatbot.py
│   ├── currency_converter.py
│   ├── data_loader.py
│   └── README.md
│
├── tests/
│   ├── test_chatbot_performance.py
│   └── README.md
│
├── .env.example
├── .gitignore
├── requirements.txt
├── web_app.py
├── test_cases.md
├── test_chatbot_e2e.py
├── test_chatbot_stage5.py
├── test_gemini.py
└── README.md
```

## 10. Installation and How to Run

### Prerequisites

- Python 3.10 or later
- Git
- Google Gemini API key

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd CSC649-Group-Project
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own Gemini API key.

**Important:** Do not upload or commit the `.env` file to GitHub.

### Step 5: Run the Application

```bash
python web_app.py
```

### Step 6: Open the Chatbot

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

The chatbot interface should now be available.

## 11. Testing

The project includes system testing and chatbot response-time performance testing.

### System Testing

The `test_cases.md` file documents eight system test cases covering:

- Travel information retrieval
- Reverse travel directions
- Gen Z slang detection
- Response relevance
- Empty input handling
- Frontend functionality
- Backend integration

### Performance Testing

The `tests/test_chatbot_performance.py` script evaluates chatbot response time across five categories:

- Travel Route
- Travel Status
- Currency Conversion
- Gen Z Slang
- General Travel

Each category is tested five times. The script calculates the average, minimum and maximum response time and exports the results to `performance_results.csv`.

To run the performance test:

```bash
python -m tests.test_chatbot_performance
```

## 12. Limitations

- Travel information retrieval depends on the coverage and accuracy of the available dataset.
- The chatbot may not provide matching transportation information for every route or travel enquiry.
- Currency conversion depends on the availability of the Frankfurter API and its exchange-rate data.
- Gemini-generated responses may occasionally contain inaccurate or incomplete information.
- The current system does not yet provide personalised travel budget allocation or expense tracking.

## 13. Generative AI (GenAI) Usage

Generative AI is integrated into the project through Google's Gemini API to support natural language response generation and general travel enquiries.

GenAI tools may also be used during development to assist with code suggestions, debugging, prompt improvements and documentation.

All AI-assisted outputs are reviewed, modified where necessary and tested by the project team.
