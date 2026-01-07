import httpx
import logging
from app.core.config import settings
from typing import Optional, Dict, Any
import json
import traceback

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.webhook_url = settings.DISCORD_WEBHOOK_URL
    
    async def send_notification(self, title: str, description: str, color: int = 0x00ff00, fields: list = None):
        """
        Discord WebhookにEmbedメッセージを送信する
        """
        if not self.webhook_url:
            logger.warning("Discord Webhook URL is not set. Skipping notification.")
            return

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields or []
        }

        payload = {
            "embeds": [embed]
        }

        try:
            # タイムアウトを10秒に延長（デフォルト5秒だとDiscord側の遅延で失敗することがある）
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # 400 Bad Requestなどの場合、Discordからのレスポンス本文に理由が書いてある
            logger.error(f"Discord Webhook returned error: {e}\nResponse body: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}", exc_info=True)

    async def notify_success(self, user_ip: str, ai_response: str, process_time: float, llm_time: float, tts_time: float):
        """成功通知"""
        # DiscordのField Valueは空だと400エラーになるため、空の場合は代替テキストを入れる
        display_response = ai_response[:1024] if ai_response and ai_response.strip() else "(No response text)"
        
        fields = [
            {
                "name": "⏳ Timings", 
                "value": f"**Total:** {process_time:.2f}s\t**LLM:** {llm_time:.2f}s\t**TTS:** {tts_time:.2f}s", 
                "inline": True
            },
            {"name": "Client", "value": user_ip, "inline": True},
            {"name": "AI Response", "value": display_response, "inline": False} # 1024文字制限対策
        ]
        await self.send_notification(
            title="✨ Audio Processed Successfully",
            description="音声処理が完了しました。",
            color=0x57F287, # Green
            fields=fields
        )

    async def notify_error(self, error: Exception, context: str = ""):
        """エラー通知"""
        tb = traceback.format_exc()
        # スタックトレースが長すぎる場合は切り詰める(Discord制限: 4096文字だが安全マージンをとる)
        if len(tb) > 1000:
            tb = tb[-1000:]
        
        description = f"**Error**: {str(error)}\n**Context**: {context}"
        
        fields = [
             {"name": "Traceback", "value": f"```python\n{tb}\n```", "inline": False}
        ]

        await self.send_notification(
            title="🚨 Server Error Occurred",
            description=description,
            color=0xED4245, # Red
            fields=fields
        )
