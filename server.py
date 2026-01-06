from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import uvicorn
import shutil
import os
import time
import base64
import requests
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- Gemini設定 ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
あなたは優秀な音声アシスタントです。以下のルールを厳守してください。
1. 返答は短く、簡潔に（1〜2文程度）。
2. 口調は親しみやすく、しかし丁寧すぎない「です・ます」調。
3. Markdown記法や絵文字、URLは一切使用しない。読み上げに適したテキストのみを出力する。
"""

# --- Whisper設定 ---
MODEL_SIZE = "medium"
print(f"Loading Whisper model ({MODEL_SIZE})...")
stt_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

# --- VOICEVOX設定 ---
VOICEVOX_HOST = "127.0.0.1" # Dockerが同じホストで動いている前提
VOICEVOX_PORT = 50021
SPEAKER_ID = 3 # 3: ずんだもん(ノーマル), 2: 四国めたん(ノーマル) 等に変更可

def generate_voice(text: str, speaker: int = SPEAKER_ID) -> bytes:
    """VOICEVOX Engineを利用してWAVデータを生成する"""
    base_url = f"http://{VOICEVOX_HOST}:{VOICEVOX_PORT}"
    
    # 1. 音声合成用のクエリを作成 (Audio Query)
    params = {"text": text, "speaker": speaker}
    res1 = requests.post(f"{base_url}/audio_query", params=params)
    if res1.status_code != 200:
        print(f"[TTS Error] Query failed: {res1.text}")
        return None
    query_data = res1.json()

    # 2. 音声合成を実行 (Synthesis)
    # 必要ならここで query_data['speedScale'] = 1.2 など速度調整が可能
    res2 = requests.post(f"{base_url}/synthesis", params={"speaker": speaker}, json=query_data)
    if res2.status_code != 200:
        print(f"[TTS Error] Synthesis failed: {res2.text}")
        return None

    return res2.content

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    total_start = time.time()
    
    # 1. STT
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    segments, _ = stt_model.transcribe(temp_filename, beam_size=5, language="ja")
    user_text = "".join([segment.text for segment in segments])
    os.remove(temp_filename)
    
    print(f"[STT] '{user_text}'")

    if not user_text.strip():
        return {"user_text": "", "ai_text": "", "audio_base64": None}

    # 2. LLM
    llm_start = time.time()
    chat_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_text,
        config={"system_instruction": SYSTEM_INSTRUCTION}
    )
    ai_text = chat_response.text.strip()
    print(f"[LLM] '{ai_text}' ({time.time() - llm_start:.2f}s)")
    
    # 3. TTS
    tts_start = time.time()
    audio_data = generate_voice(ai_text)
    print(f"[TTS] Generated ({time.time() - tts_start:.2f}s)")
    
    audio_base64 = None
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    total_time = time.time() - total_start
    print(f"Total processing time: {total_time:.2f}s")

    return {
        "user_text": user_text,
        "ai_text": ai_text,
        "audio_base64": audio_base64
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)