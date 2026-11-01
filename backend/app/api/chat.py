import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.agent import stream_answer
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter()

def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

def stream_events(messages: list[dict]):
    try:
        for text in stream_answer(messages):
            yield sse_event({"type": "token", "text": text})
    except Exception:
        logger.exception("Error while streaming the answer")
        yield sse_event({"type": "error", "text": "Something went wrong. Please try again."})
    yield sse_event({"type": "done"})

@router.post("/chat")
def chat(request: ChatRequest):
    messages = [message.model_dump() for message in request.messages]
    return StreamingResponse(stream_events(messages), media_type="text/event-stream")