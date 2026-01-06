from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import uvicorn
import shutil
import os
import time

app = FastAPI()

# --- 設定 ---
# model_size: "tiny", "base", "small", "medium", "large-v3"
# CPU推論の場合は "int8" で十分な精度と速度が出ます
MODEL_SIZE = "medium"
print(f"Loading Whisper model ({MODEL_SIZE})...")

# モデルのロード（サーバー起動時に1回だけ実行）
# device="cpu" を明示。もしGPUがあるなら "cuda" に変更
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    start_time = time.time()
    
    # 1. 一時ファイル保存
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. STT (Speech to Text)
    # beam_size=5 は精度重視。速度重視なら1にする
    segments, info = model.transcribe(temp_filename, beam_size=5, language="ja")
    
    text = "".join([segment.text for segment in segments])
    
    # 3. 後始末
    os.remove(temp_filename)
    
    duration = time.time() - start_time
    print(f"[STT] Detected: '{text}' ({duration:.2f}s)")
    
    # 現段階ではテキストのみを返す
    return {"text": text}

if __name__ == "__main__":
    # host="0.0.0.0" で外部（RasPi）からのアクセスを許可
    uvicorn.run(app, host="0.0.0.0", port=8000)