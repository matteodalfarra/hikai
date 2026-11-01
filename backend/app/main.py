from fastapi import FastAPI

from app.api import chat

app = FastAPI()
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok"}