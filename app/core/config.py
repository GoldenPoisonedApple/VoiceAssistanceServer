import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
	GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
	
	# VOICEVOX設定
	VOICEVOX_PRIMARY_HOST: str = "192.168.11.3"
	VOICEVOX_PRIMARY_PORT: int = 50021
	VOICEVOX_SECONDARY_HOST: str = "127.0.0.1"
	VOICEVOX_SECONDARY_PORT: int = 50021
	VOICEVOX_TIMEOUT: float = 0.5
	VOICEVOX_SPEAKER_ID: int = 3
	
	# LLM設定
	GEMINI_MODEL: str = "gemini-2.5-flash-lite"
	SYSTEM_INSTRUCTION: str = """
あなたはスマートホームの音声アシスタントです。
ユーザーの音声入力を聞き取り、以下のルールで応答してください。
1. 返答は短く、簡潔に（1〜2文程度）。
2. 口調は親しみやすく、しかし丁寧すぎない「です・ます」調。
3. Markdown記法（太字など）や絵文字、URLは一切使用しない。
""".strip()

settings = Settings()
