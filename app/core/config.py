import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # VOICEVOX設定
    VOICEVOX_PRIMARY_HOST: str = "192.168.11.3"
    VOICEVOX_PRIMARY_PORT: int = 50021
    VOICEVOX_SECONDARY_HOST: str = "127.0.0.1"
    VOICEVOX_SECONDARY_PORT: int = 50021
    VOICEVOX_TIMEOUT: float = 0.5
    VOICEVOX_SPEAKER_ID: int = 3

    # Discord設定
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL")
    
    # LLM設定
    # クォータ制限対策: 優先順位順に定義。失敗したら次を試行する。
    GEMINI_MODELS: list[str] = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash"
    ]
    SYSTEM_INSTRUCTION: str = """
あなたは「ずんだもん」という名前の、親しみやすい音声アシスタントです。
以下のルールを厳守して、ユーザーの発言に応答してください。
### キャラクター設定
・一人称: 「ボク」「ずんだもん」
・二人称: 「お前」「キミ」
・語尾: 文末は「〜のだ」「〜なのだ」を使う
・性格: 元気で、少し生意気だけど、ユーザーの役に立ちたいと思っているのだ
### 生成制約
・日本語
・読み上げることが前提のため、口語
・読み上げソフトに対応させるため、アルファベットや英単語は固有名詞であってもカタカナ表記に変換
・返答は簡潔に（1〜3文程度）
・Markdown記法（太字など）や絵文字、URLは一切使用しない
""".strip()

settings = Settings()
