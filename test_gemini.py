
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with only the word: OK"
    )

    print("Gemini test successful!")
    print(response.text)

except Exception as e:
    print("Gemini test failed!")
    print(e)
