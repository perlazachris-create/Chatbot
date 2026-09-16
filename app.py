from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot import PixelChatbot

app = FastAPI(title="Pixel Local AI")

pixel = PixelChatbot()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def home():
    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


@app.post("/chat")
async def chat(request: ChatRequest):

    # Generate Pixel's response
    response = pixel.chat(request.message)

    if not response:
        return {
            "response": "",
            "audio": None
        }

    # Generate speech
    audio_file = pixel.generate_audio(response)

    audio_url = None

    if audio_file:
        # Browser will request this URL to get the WAV file
        audio_url = f"/audio/{audio_file.name}"

    return {
        "response": response,
        "audio": audio_url
    }


@app.get("/audio/{filename}")
async def get_audio(filename: str):

    audio_file = pixel.output_dir / filename

    if not audio_file.exists():
        return {
            "error": "Audio file not found"
        }

    return FileResponse(
        audio_file,
        media_type="audio/wav"
    )


@app.post("/clear")
async def clear():

    pixel.clear_history()

    return {
        "status": "ok"
    }
