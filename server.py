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
# デスクトップPC (GPU) のIPアドレス
PRIMARY_HOST = "192.168.11.3"  # ★環境に合わせて変更してください
PRIMARY_PORT = 50021

# ローカルサーバー (CPU) のIPアドレス
SECONDARY_HOST = "127.0.0.1"
SECONDARY_PORT = 50021

TIMEOUT = 0.5	# VOICEVOXサーバーへの接続タイムアウト（秒）
SPEAKER_ID = 3 # ずんだもん

def request_tts(host: str, port: int, text: str, speaker: int, timeout: float = None) -> bytes:
    """指定されたホストのVOICEVOX Engineにリクエストを送る"""
    base_url = f"http://{host}:{port}"
    try:
        # 1. Audio Query
        # ホストが生きてるかのチェックも兼ねてtimeoutを設定
        params = {"text": text, "speaker": speaker}
        res1 = requests.post(f"{base_url}/audio_query", params=params, timeout=timeout)
        res1.raise_for_status()
        query_data = res1.json()

        # 2. Synthesis
        # 合成処理自体は時間がかかるため、timeoutは少し長めにとるか、Noneにする
        # ただし、そもそもホストが生きてるかのチェックはqueryで済んでいる
        res2 = requests.post(f"{base_url}/synthesis", params={"speaker": speaker}, json=query_data, timeout=None)
        res2.raise_for_status()
        return res2.content
    except Exception as e:
        # 呼び出し元でキャッチさせるために例外を再送出
        raise e

def generate_voice(text: str, speaker: int = SPEAKER_ID) -> bytes:
    # 1. まずはデスクトップPC (GPU) にトライ
    try:
        # 接続確認も兼ねてAudioQueryを投げる。
        # 0.2秒で繋がらなければPCは落ちているとみなす。
        print(f"[TTS] Trying GPU Server ({PRIMARY_HOST})...")
        return request_tts(PRIMARY_HOST, PRIMARY_PORT, text, speaker, timeout=TIMEOUT)
    except Exception as e:
        print(f"[TTS] GPU Server unreachable or failed: {e}")
        print("[TTS] Falling back to Local CPU Server...")

    # 2. ダメならローカル (CPU) で実行
    try:
        return request_tts(SECONDARY_HOST, SECONDARY_PORT, text, speaker, timeout=None)
    except Exception as e:
        print(f"[TTS Error] Local fallback also failed: {e}")
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
            model="gemini-2.5-flash-lite",
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