from fastapi import FastAPI
from app.routers import audio
import logging

# ロギング設定
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()

app.include_router(audio.router)

@app.get("/")
def health_check():
	return {"status": "ok"}
