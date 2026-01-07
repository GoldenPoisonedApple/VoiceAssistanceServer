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

## サービス(デーモン)化
```bash
sudo nano /etc/systemd/system/shizuku-server.service
```
で以下
```toml
[Unit]
Description=Shizuku Voice Assistant Server
After=network.target

[Service]
# 実行ユーザーとグループ
User=vermouth
Group=vermouth

# 作業ディレクトリ (.envの読み込みや相対パス解決に必須)
WorkingDirectory=/home/vermouth/Programs/ShizukuServer

# 実行コマンド (仮想環境内のPythonを絶対パスで指定)
ExecStart=/home/vermouth/Programs/ShizukuServer/.venv/bin/python server.py

# プロセスが落ちた場合に自動再起動する (5秒待機後)
Restart=always
RestartSec=5

# ログ出力設定 (journalctlで確認可能にする)
SyslogIdentifier=shizuku-server
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

- サービスの有効化
```bash
# 1. Systemdの設定リロード（ファイル作成・変更時は必須）
sudo systemctl daemon-reload

# 2. 自動起動の有効化（OS再起動時に勝手に立ち上がるように設定）
sudo systemctl enable shizuku-server

# 3. サービスの即時起動
sudo systemctl start shizuku-server

# 4. ステータス確認
sudo systemctl status shizuku-server
```

- ログ監視
```bash
sudo journalctl -u shizuku-server -f
```

- コードを変更した場合
```bash
sudo systemctl restart shizuku-server
```