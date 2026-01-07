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
		try:
			response = self.client.models.generate_content(
				model=settings.GEMINI_MODEL,
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
			return response.text.strip()
		except Exception as e:
			logger.error(f"LLM Error: {e}")
			raise e
