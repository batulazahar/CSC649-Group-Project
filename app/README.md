\# Frontend (app)



This folder contains the frontend components of the Travel Budget Management Chatbot. It provides the user interface where users can interact with the chatbot.



\## 1. Folder Structure



```text

app/

├── static/

│   ├── css/

│   │   └── style.css

│   └── js/

│       └── script.js

├── templates/

│   └── index.html

└── README.md

```



\## 2. Frontend Components



\### 2.1 index.html



Defines the structure and elements of the chatbot web interface.



\### 2.2 style.css



Controls the appearance and layout of the chatbot interface, including colours, spacing, typography and responsive styling.



\### 2.3 script.js



Handles frontend interactions, including:

\- Capturing user messages.

\- Sending user questions to the Flask `/chat` endpoint.

\- Receiving chatbot responses.

\- Displaying messages in the chat interface.



\## 3. Technologies Used



\- HTML

\- CSS

\- JavaScript

\- Flask API integration



\## 4. Frontend and Backend Communication



The frontend communicates with the Flask backend through the `/chat` endpoint using HTTP POST requests.



The backend processes the user's message and returns the chatbot response in JSON format, which is then displayed in the chat interface.

