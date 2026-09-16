# Pixel — Local AI Voice Chatbot

Pixel is a locally hosted AI chatbot that uses **LM Studio** for language generation and **Audio8 TTS** for voice synthesis.

The project provides a simple web interface where users can chat with Pixel through a browser.

The goal is to eventually provide a real-time conversational experience where Pixel's responses are generated and spoken as they are produced.

---

## Features

* Local AI inference through LM Studio
* Custom Pixel personality/system prompt
* Conversation memory
* Web-based chat interface
* FastAPI backend
* Audio8 text-to-speech integration
* WAV audio generation
* Browser-based audio playback
* Runs locally without requiring a cloud AI service

---

## Architecture

The current project is organized into several components:

```text
                    ┌─────────────────┐
                    │     Browser     │
                    │                 │
                    │  HTML / CSS /   │
                    │      JS         │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ▼
                    ┌─────────────────┐
                    │     app.py      │
                    │     FastAPI     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   chatbot.py    │
                    │  PixelChatbot   │
                    └───────┬─┬───────┘
                            │ │
                  ┌─────────┘ └─────────┐
                  ▼                     ▼
          ┌───────────────┐     ┌───────────────┐
          │   LM Studio   │     │    Audio8     │
          │      LLM      │     │      TTS      │
          └───────────────┘     └───────┬───────┘
                                        │
                                        ▼
                                   WAV Audio
                                        │
                                        ▼
                                    Browser
                                        │
                                        ▼
                                    Speakers
```

---

## Project Structure

```text
PIXEL/
│
├── app.py
├── chatbot.py
├── README.md
│
├── templates/
│   └── index.html
│
├── static/
│   ├── app.js
│   └── style.css
│
└── audio_output/
    └── generated WAV files
```

---

## Components

### `chatbot.py`

Contains the main Pixel chatbot logic.

Responsibilities include:

* Connecting to LM Studio
* Maintaining conversation history
* Sending user messages to the LLM
* Receiving the generated response
* Sending text to Audio8
* Saving generated speech as WAV files
* Clearing conversation history

The main class is:

```python
PixelChatbot
```

---

### `app.py`

`app.py` is the web server and acts as the bridge between the browser and `chatbot.py`.

It uses:

* FastAPI
* Pydantic
* Static file serving

Main endpoints:

```text
GET  /
POST /chat
POST /clear
GET  /audio/{filename}
```

#### `GET /`

Loads the web interface.

#### `POST /chat`

Receives a user's message, sends it to Pixel, generates the response, and requests TTS audio.

Example request:

```json
{
    "message": "Hello Pixel"
}
```

Example response:

```json
{
    "response": "Hah. Took you long enough.",
    "audio": "/audio/pixel_xxxxx.wav"
}
```

#### `POST /clear`

Clears Pixel's conversation memory.

#### `GET /audio/{filename}`

Serves generated WAV files to the browser.

---

## Web Interface

### `templates/index.html`

Contains the structure of the user interface.

The current interface includes:

* Pixel header
* Chat message area
* User messages
* Pixel messages
* Text input
* Send button

---

### `static/style.css`

Controls the appearance of the web interface.

The current design uses:

* Dark
