from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request, BackgroundTasks
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.services.notification_service import NotificationService
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

@lru_cache()
def get_notification_service():
    return NotificationService()

@router.post("/process-audio")
async def process_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service),
    notification_service: NotificationService = Depends(get_notification_service)
):
    try:
        total_start = time.time()
        
        file_bytes = await file.read()
        
        # 1. LLM (Audio -> Text & Response)
        logger.info("Sending audio to Gemini...")
        llm_start = time.time()
        
        ai_text = llm_service.generate_response(file_bytes)
        
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

        # 成功通知 (Background)
        client_host = request.client.host if request.client else "Unknown"
        background_tasks.add_task(
            notification_service.notify_success,
            user_ip=client_host,
            ai_response=ai_text,
            process_time=total_time,
            llm_time=llm_duration,
            tts_time=tts_duration
        )

        return {
            "user_text": "(Audio Input)", 
            "ai_text": ai_text,
            "audio_base64": audio_base64
        }
    except Exception as e:
        logger.error(f"Error in process_audio: {e}", exc_info=True)
        
        # エラー通知 (BackgroundTasksはレスポンス返却後に走るため、raiseすると実行されない可能性がある)
        # 確実に通知するために、notification_serviceを直接呼ぶ
        try:
            await notification_service.notify_error(error=e, context="process_audio")
        except Exception as notify_err:
             # 通知自体が失敗してもメイン処理のエラーを隠さないようにする
            logger.error(f"Failed to send error notification: {notify_err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
