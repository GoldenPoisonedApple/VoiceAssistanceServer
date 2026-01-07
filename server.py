from fastapi import FastAPI, UploadFile, File
import uvicorn
import time
import base64
import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- Gemini設定 ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

# 音声入力に対するシステムプロンプト
SYSTEM_INSTRUCTION = """
あなたはスマートホームの音声アシスタントです。
ユーザーの音声入力を聞き取り、以下のルールで応答してください。
1. 返答は短く、簡潔に（1〜2文程度）。
2. 口調は親しみやすく、しかし丁寧すぎない「です・ます」調。
3. Markdown記法（太字など）や絵文字、URLは一切使用しない。
"""

# --- VOICEVOX設定 ---
VOICEVOX_HOST = "127.0.0.1"
VOICEVOX_PORT = 50021
SPEAKER_ID = 3 # ずんだもん

def generate_voice(text: str, speaker: int = SPEAKER_ID) -> bytes:
    base_url = f"http://{VOICEVOX_HOST}:{VOICEVOX_PORT}"
    try:
        # Audio Query
        params = {"text": text, "speaker": speaker}
        res1 = requests.post(f"{base_url}/audio_query", params=params)
        res1.raise_for_status()
        query_data = res1.json()

        # Synthesis
        res2 = requests.post(f"{base_url}/synthesis", params={"speaker": speaker}, json=query_data)
        res2.raise_for_status()
        return res2.content
    except Exception as e:
        print(f"[TTS Error] {e}")
        return None

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    total_start = time.time()
    
    # 音声ファイルをメモリ上に読み込む
    file_bytes = await file.read()
    
    # 1. LLM (Audio -> Text & Response)
    print("Sending audio to Gemini...")
    llm_start = time.time()
    
    try:
        # Gemini 1.5 Flash に音声とプロンプトを同時に投げる
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=file_bytes, mime_type="audio/wav"),
                        types.Part.from_text(text="この発言に応答してください。")
                    ]
                )
            ],
            config={
                "system_instruction": SYSTEM_INSTRUCTION
            }
        )
        ai_text = response.text.strip()
    except Exception as e:
        print(f"[LLM Error] {e}")
        return {"user_text": "Error", "ai_text": "エラーが発生しました。", "audio_base64": None}

    llm_duration = time.time() - llm_start
    print(f"[LLM] '{ai_text}' ({llm_duration:.2f}s)")
    
    # 2. TTS (Voicevox)
    tts_start = time.time()
    audio_data = generate_voice(ai_text)
    tts_duration = time.time() - tts_start
    print(f"[TTS] Generated ({tts_duration:.2f}s)")
    
    audio_base64 = None
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    total_time = time.time() - total_start
    print(f"Total processing time: {total_time:.2f}s")

    return {
        "user_text": "(Audio Input)", # STTをスキップしたためテキスト化はされません
        "ai_text": ai_text,
        "audio_base64": audio_base64
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)