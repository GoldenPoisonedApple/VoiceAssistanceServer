## 仮想環境
```bash
python3 -m venv venv
source ./venv/bin/activate
```

## 依存ライブラリ
```bash
# faster-whisper: 高速推論エンジン
# fastapi, uvicorn: APIサーバー
# python-multipart: ファイルアップロード処理に必要
pip install faster-whisper fastapi uvicorn python-multipart python-dotenv
# LLM API
pip install -q -U google-genai
# requests
pip install requests
```

wisperに時間かかってる気がする
音声ファイルをLLMに投げた方が早いのでは？
```bash
(venv) vermouth@ubuntu-dev:~/Programs/ShizukuServer$ python server.py
Loading Whisper model (medium)...
INFO:     Started server process [2293122]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
[STT] 'じゃあ、今日の天気何?' (9.22s)
[LLM] '今日の天気は曇りで、最高気温は25度です。' (1.12s)
```
