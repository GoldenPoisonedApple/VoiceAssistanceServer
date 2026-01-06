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
```
