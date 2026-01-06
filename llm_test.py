from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
	raise ValueError("GEMINI_API_KEY environment variable not set")



# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
	model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)