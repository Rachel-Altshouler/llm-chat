import json
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from client import ask_model

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


def trim_history(messages: list[dict], keep_last: int = 12) -> list[dict]:
    """Keep only the last messages so long conversations don't grow the cost forever."""
    trimmed = messages[-keep_last:]
    # Start the trimmed history with a user message
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
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages is empty")
    for m in req.messages:
        if m.role not in ("user", "assistant"):
            raise HTTPException(status_code=400, detail=f"invalid role: {m.role}")

    def generate():
        try:
            history = trim_history([m.model_dump() for m in req.messages])
            for event in ask_model(history):
                yield sse(event)
            yield sse({"type": "done"})
        except Exception as e:
            # Full error details in the server terminal, short message to the page
            traceback.print_exc()
            yield sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
