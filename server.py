from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import uvicorn
import shutil
import os
import time
from google import genai
from dotenv import load_dotenv

# 環境変数を.envファイルからロード
load_dotenv()

app = FastAPI()

# --- Gemini設定 ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

# 音声対話に特化したシステムプロンプト
# Markdownや絵文字はTTSで読み上げられない/邪魔になるため禁止します
SYSTEM_INSTRUCTION = """
あなたは優秀な音声アシスタントです。以下のルールを厳守してください。
1. 返答は短く、簡潔に（1〜2文程度）。
2. 口調は親しみやすく、しかし丁寧すぎない「です・ます」調。
3. Markdown記法（**太字**など）や絵文字は一切使用しない。
4. URLやコードブロックを含めない。読み上げに適したテキストのみを出力する。
"""

# --- Whisper設定 ---
MODEL_SIZE = "medium"
print(f"Loading Whisper model ({MODEL_SIZE})...")
stt_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    start_time = time.time()
    
    # 1. 一時ファイル保存
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. STT (Speech to Text)
    segments, info = stt_model.transcribe(temp_filename, beam_size=5, language="ja")
    user_text = "".join([segment.text for segment in segments])
    os.remove(temp_filename)
    
    stt_duration = time.time() - start_time
    print(f"[STT] '{user_text}' ({stt_duration:.2f}s)")

    # 3. LLM (Gemini Inference)
    if not user_text.strip():
        return {"text": "", "response": "音声が聞き取れませんでした。"}

    llm_start = time.time()
    chat_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_text,
        config={
            "system_instruction": SYSTEM_INSTRUCTION
        }
    )
    ai_text = chat_response.text.strip() # 余計な空白除去
    
    llm_duration = time.time() - llm_start
    print(f"[LLM] '{ai_text}' ({llm_duration:.2f}s)")
    
    # クライアントにはユーザーの認識結果とAIの返答の両方を返す
    return {
        "user_text": user_text,
        "ai_text": ai_text
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)