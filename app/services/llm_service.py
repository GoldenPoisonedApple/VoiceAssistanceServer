from google import genai
from google.genai import types
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
	def __init__(self):
		if not settings.GEMINI_API_KEY:
			raise ValueError("GEMINI_API_KEY is not set")
		self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

	def generate_response(self, audio_bytes: bytes, prompt_text: str = "この発言に応答してください。") -> str:
		last_exception = None

		# 定義されたモデル順に試行する
		for model_name in settings.GEMINI_MODELS:
			try:
				# logger.info(f"Trying LLM model: {model_name}")
				
				response = self.client.models.generate_content(
					model=model_name,
					contents=[
						types.Content(
							parts=[
								types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
								types.Part.from_text(text=prompt_text)
							]
						)
					],
					config={
						"system_instruction": settings.SYSTEM_INSTRUCTION
					}
				)
				
				# 成功したらモデル名をログに残してリターン
				logger.info(f"Generated response using model: {model_name}")
				return response.text.strip()

			except Exception as e:
				# 429 RESOURCE_EXHAUSTED などのエラーが発生した場合
				logger.warning(f"Model {model_name} failed: {e}")
				last_exception = e
				# 次のモデルへフォールバック (continue)

		# 全てのモデルで失敗した場合
		logger.error("All Gemini models failed.")
		if last_exception:
			raise last_exception
		else:
			raise Exception("No available Gemini models")
