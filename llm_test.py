from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
	raise ValueError("GEMINI_API_KEY environment variable not set")

# 音声対話に特化したシステムプロンプト
SYSTEM_INSTRUCTION = """
あなたは優秀な音声アシスタントです。以下のルールを厳守してください。
1. 返答は短く、簡潔に（1〜2文程度）。
2. 口調は親しみやすく、しかし丁寧すぎない「です・ます」調。
3. Markdown記法（**太字**など）や絵文字は一切使用しない。
4. URLやコードブロックを含めない。読み上げに適したテキストのみを出力する。
"""

## Create the LLM model with the specified system instruction
llm_model = genai.GenerativeModel(
	model_name="gemini-2.5-flash",
	system_instruction=SYSTEM_INSTRUCTION
)

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client()

# response = client.models.generate_content(
# 	model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)