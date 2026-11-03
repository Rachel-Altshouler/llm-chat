import json
import traceback
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from client import ask_model

app = FastAPI()


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


def trim_history(messages: list[dict], keep_last: int = 12) -> list[dict]:
    trimmed = messages[-keep_last:]
    if trimmed and trimmed[0]["role"] == "assistant":
        trimmed = trimmed[1:]
    return trimmed


def sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: ChatRequest):
    history = trim_history([m.model_dump() for m in req.messages])

    def generate():
        try:
            for event in ask_model(history):
                yield sse(event)
        except Exception as e:
            traceback.print_exc()
            yield sse({"type": "error", "message": str(e)})

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
