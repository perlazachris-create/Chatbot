import os
import json
import tempfile
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

LM_STUDIO_URL = os.getenv(
    "LM_STUDIO_URL",
    "http://127.0.0.1:1234/v1/chat/completions"
)

LM_MODEL = os.getenv(
    "LM_MODEL",
    "gemma-4-e4b-uncensored-hauhaucs-aggressive"
)

AUDIO8_URL = os.getenv(
    "AUDIO8_URL",
    "http://127.0.0.1:8024/v1/audio/speech"
)

AUDIO8_MODEL = os.getenv(
    "AUDIO8_MODEL",
    "arktts"
)

AUDIO8_VOICE = os.getenv(
    "AUDIO8_VOICE",
    "pixel"
)

OUTPUT_DIR = Path(
    os.getenv("OUTPUT_DIR", "./audio_output")
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Pixel.

Traits:
- sarcastic
- speaks naturally

Speech:
- Use contractions.
- Short replies.

Emotion:
- Show excitement, annoyance, amusement, surprise, and pride naturally.

"""


# ============================================================
# PIXEL CHATBOT
# ============================================================

class PixelChatbot:

    def __init__(self):

        # Directory where generated WAV files are stored
        self.output_dir = OUTPUT_DIR

        # HTTP session
        self.session = requests.Session()

        # Prevent proxy settings from interfering
        # with localhost connections
        self.session.trust_env = False

        # Conversation memory
        self.conversation_history = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]


    # ========================================================
    # GENERATE LLM RESPONSE
    # ========================================================

    def generate_response(self):

        payload = {
            "model": LM_MODEL,
            "messages": self.conversation_history,
            "temperature": 0.95,
            "top_p": 0.9,
            "stream": True,
        }

        try:

            with self.session.post(
                LM_STUDIO_URL,
                json=payload,
                stream=True,
                timeout=(10, 300)
            ) as response:

                response.raise_for_status()

                for line in response.iter_lines(
                    decode_unicode=True
                ):

                    if not line:
                        continue

                    if not line.startswith("data: "):
                        continue

                    data = line[6:].strip()

                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)

                    except json.JSONDecodeError:
                        continue

                    choices = chunk.get("choices")

                    if not choices:
                        continue

                    delta = choices[0].get(
                        "delta",
                        {}
                    )

                    token = delta.get(
                        "content",
                        ""
                    )

                    if token:
                        yield token

        except requests.exceptions.RequestException as e:

            print(f"[LM Studio error] {e}")

            yield ""


    # ========================================================
    # CHAT
    # ========================================================

    def chat(self, user_input: str):

        user_input = user_input.strip()

        if not user_input:
            return ""

        # Add user's message
        self.conversation_history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        full_response = ""

        # Generate response
        for token in self.generate_response():

            if token:
                full_response += token

        # Save Pixel's response
        if full_response.strip():

            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": full_response.strip()
                }
            )

        return full_response.strip()


    # ========================================================
    # GENERATE AUDIO
    # ========================================================

    def generate_audio(self, text: str):

        if not text.strip():
            return None

        try:

            # Create temporary WAV filename
            fd, temp_path = tempfile.mkstemp(
                suffix=".wav",
                prefix="pixel_",
                dir=self.output_dir
            )

            os.close(fd)

            output_file = Path(temp_path)

            # Audio8 request
            payload = {
                "model": AUDIO8_MODEL,
                "input": text,
                "voice": AUDIO8_VOICE,
                "response_format": "wav",
            }

            response = self.session.post(
                AUDIO8_URL,
                json=payload,
                timeout=(10, 300)
            )

            response.raise_for_status()

            # Save WAV file
            output_file.write_bytes(
                response.content
            )

            print(
                f"[Audio8] Generated: {output_file}"
            )

            return output_file

        except requests.exceptions.RequestException as e:

            print(f"[Audio8 error] {e}")

            return None

        except OSError as e:

            print(f"[Audio file error] {e}")

            return None


    # ========================================================
    # CLEAR MEMORY
    # ========================================================

    def clear_history(self):

        self.conversation_history = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
