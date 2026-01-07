import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class TTSService:
	def _request_tts(self, host: str, port: int, text: str, speaker: int, timeout: float = None) -> bytes:
		base_url = f"http://{host}:{port}"
		params = {"text": text, "speaker": speaker}
		
		try:
			# 1. Audio Query
			res1 = requests.post(f"{base_url}/audio_query", params=params, timeout=timeout)
			res1.raise_for_status()
			query_data = res1.json()

			# 2. Synthesis
			# 合成処理自体は時間がかかるため、timeoutはNone推奨
			res2 = requests.post(f"{base_url}/synthesis", params={"speaker": speaker}, json=query_data, timeout=None)
			res2.raise_for_status()
			return res2.content
		except Exception as e:
			raise e

	def generate_voice(self, text: str) -> bytes:
		# 1. Try Primary (GPU)
		try:
			logger.info(f"Trying Primary TTS Server: {settings.VOICEVOX_PRIMARY_HOST}")
			return self._request_tts(
				settings.VOICEVOX_PRIMARY_HOST, 
				settings.VOICEVOX_PRIMARY_PORT, 
				text, 
				settings.VOICEVOX_SPEAKER_ID, 
				timeout=settings.VOICEVOX_TIMEOUT
			)
		except Exception as e:
			logger.warning(f"Primary TTS Server failed: {e}")
		
		# 2. Fallback to Secondary (CPU)
		try:
			logger.info(f"Falling back to Secondary TTS Server: {settings.VOICEVOX_SECONDARY_HOST}")
			return self._request_tts(
				settings.VOICEVOX_SECONDARY_HOST, 
				settings.VOICEVOX_SECONDARY_PORT, 
				text, 
				settings.VOICEVOX_SPEAKER_ID, 
				timeout=None
			)
		except Exception as e:
			logger.error(f"Secondary TTS Server failed: {e}")
			return None
