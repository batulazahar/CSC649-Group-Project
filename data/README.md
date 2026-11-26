\# Data Folder



This folder contains the datasets used by the Travel Budget Management Chatbot to support travel information retrieval and Gen Z slang explanations.



\## 1. Travel Dataset



\*\*File:\*\* `travel\_dataset\_verified.csv`



\- \*\*Source:\*\* Kaggle

\- \*\*Total Records:\*\* 497

\- \*\*Purpose:\*\* Provides travel-related questions and answers for transportation information retrieval.

\- \*\*Columns:\*\*

&#x20; - `query`: User's travel-related question.

&#x20; - `intent`: The category or purpose of the question.

&#x20; - `entities`: Extracted information such as source, destination, date and transport mode.

&#x20; - `response`: The corresponding chatbot response.



\## 2. Gen Z Slang Dataset



\*\*File:\*\* `genz\_slang.csv`



\- \*\*Source:\*\* Kaggle

\- \*\*Total Records:\*\* 145

\- \*\*Purpose:\*\* Provides Gen Z slang keywords and their meanings.

\- \*\*Columns:\*\*

&#x20; - `keyword`: Gen Z slang term.

&#x20; - `description`: Explanation of the slang term.



\## 3. Additional Dataset



\*\*File:\*\* `TransitChat-Conversational\_Route\_and\_Schedule\_Dataset (1).csv`



This is an additional dataset stored in the project directory. It is not currently loaded by the chatbot application.



\## 4. Dataset Usage



The active datasets are loaded by `src/data\_loader.py` using pandas.



The chatbot uses:

\- The travel dataset for travel information retrieval.

\- The Gen Z slang dataset for identifying and explaining slang terms.



\*\*Note:\*\* The original Kaggle dataset links can be added here for reference.

