# ShizukuServer

ShizukuServerは、スマートホーム向けの音声アシスタントバックエンドサーバーです。
ユーザーの音声入力を受け取り、Google Gemini (LLM) で応答を生成し、VOICEVOX (TTS) で音声を合成して返します。

## 機能

- **音声対話機能**: ユーザーの音声を直接 Gemini に送信し、音声認識と応答生成を一括で行います (Multimodal)。
- **音声合成 (TTS)**: 生成された応答テキストを VOICEVOX で読み上げます。
- **冗長構成**: VOICEVOX サーバーへの接続において、メインサーバー (GPU想定) が応答しない場合、自動的にローカルサーバー (CPU想定) へフォールバックします。

## 必要要件

- Python 3.10+
- VOICEVOX Engine (Docker または アプリ版)
- Google Gemini API Key

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd ShizukuServer
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env` ファイルを作成し、Gemini APIキーを設定してください。

```bash
touch .env
```

**.env**:
```properties
GEMINI_API_KEY=your_api_key_here
```

### 4. VOICEVOXの設定

`app/core/config.py` 内で VOICEVOX サーバーのアドレスを設定可能です。
デフォルトでは以下のように構成されています。

- **Primary (GPU)**: `192.168.11.3:50021`
- **Secondary (Local)**: `127.0.0.1:50021`

環境に合わせて変更してください。

## 起動方法

### 開発・実行

```bash
python server.py
# または
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API仕様

### `POST /process-audio`

音声ファイルをアップロードし、AIの応答（テキストおよび音声）を取得します。

- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: 音声ファイル (`audio/wav` 推奨)

#### レスポンス例 (成功時)

```json
{
  "user_text": "(Audio Input)",
  "ai_text": "はい、電気をつけました。",
  "audio_base64": "UklGRi..."
}
```

#### エラーハンドリング

本サーバーは標準的なHTTPステータスコードを使用します。

- **200 OK**: 成功。`audio_base64` が `null` の場合は音声合成のみ失敗しています（テキストは利用可能）。
- **500 Internal Server Error**: LLMの生成失敗やサーバー内部エラー。

```json
{
  "detail": "Internal Server Error"
}
```
