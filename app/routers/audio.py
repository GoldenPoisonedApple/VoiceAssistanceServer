from fastapi import APIRouter, UploadFile, File, Depends
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from functools import lru_cache
import base64
import time
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
@lru_cache()
def get_llm_service():
    return LLMService()

@lru_cache()
def get_tts_service():
	return TTSService()

@router.post("/process-audio")
async def process_audio(
	file: UploadFile = File(...),
	llm_service: LLMService = Depends(get_llm_service),
	tts_service: TTSService = Depends(get_tts_service)
):
	total_start = time.time()
	
	file_bytes = await file.read()
	
	# 1. LLM (Audio -> Text & Response)
	logger.info("Sending audio to Gemini...")
	llm_start = time.time()
	
	try:
		ai_text = llm_service.generate_response(file_bytes)
	except Exception:
		# エラー発生時のフォールバックレスポンス
		return {"user_text": "Error", "ai_text": "エラーが発生しました。", "audio_base64": None}

	llm_duration = time.time() - llm_start
	logger.info(f"LLM Response: '{ai_text}' ({llm_duration:.2f}s)")
	
	# 2. TTS (Voicevox)
	tts_start = time.time()
	audio_data = tts_service.generate_voice(ai_text)
	tts_duration = time.time() - tts_start
	logger.info(f"TTS Generated ({tts_duration:.2f}s)")
	
	audio_base64 = None
	if audio_data:
		audio_base64 = base64.b64encode(audio_data).decode("utf-8")

	total_time = time.time() - total_start
	logger.info(f"Total processing time: {total_time:.2f}s")

	return {
		"user_text": "(Audio Input)", 
		"ai_text": ai_text,
		"audio_base64": audio_base64
	}
