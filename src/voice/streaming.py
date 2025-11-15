"""
Voice streaming using Gemini Live API for low-latency audio I/O
"""

import asyncio
import websockets
import json
from typing import AsyncGenerator, Optional, Callable
import os


class VoiceStreamer:
    """
    Handles bidirectional voice streaming using Gemini Live API.

    This provides low-latency voice input/output for the orchestrator.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-live-001",
    ):
        """
        Initialize the voice streamer.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model to use for streaming
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.websocket = None

        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable."
            )

    async def connect(self):
        """
        Connect to Gemini Live API via WebSocket.
        """
        # Gemini Live API WebSocket endpoint
        # Note: This is a placeholder - actual endpoint will be from Google docs
        ws_url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"

        try:
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key,
                },
            )
            print("[Voice] Connected to Gemini Live API")
        except Exception as e:
            print(f"[Voice] Connection failed: {e}")
            raise

    async def disconnect(self):
        """
        Disconnect from the WebSocket.
        """
        if self.websocket:
            await self.websocket.close()
            print("[Voice] Disconnected from Gemini Live API")

    async def stream_audio_input(
        self, audio_generator: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """
        Stream audio input to Gemini and receive text transcription.

        Args:
            audio_generator: Async generator yielding audio chunks

        Yields:
            Transcribed text chunks
        """
        if not self.websocket:
            await self.connect()

        try:
            async for audio_chunk in audio_generator:
                # Send audio to Gemini
                message = {
                    "realtime_input": {
                        "media_chunks": [
                            {
                                "mime_type": "audio/pcm",
                                "data": audio_chunk.hex(),
                            }
                        ]
                    }
                }
                await self.websocket.send(json.dumps(message))

                # Receive transcription
                response = await self.websocket.recv()
                data = json.loads(response)

                # Extract text from response
                if "serverContent" in data:
                    for part in data["serverContent"].get("modelTurn", {}).get(
                        "parts", []
                    ):
                        if "text" in part:
                            yield part["text"]

        except Exception as e:
            print(f"[Voice] Streaming error: {e}")
            yield f"[Error: {str(e)}]"

    async def stream_text_to_audio(
        self, text: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Convert text to audio using Gemini's voice output.

        Args:
            text: Text to convert to speech

        Yields:
            Audio chunks
        """
        if not self.websocket:
            await self.connect()

        try:
            # Send text for TTS
            message = {
                "client_content": {
                    "turns": [{"role": "user", "parts": [{"text": text}]}],
                    "turn_complete": True,
                }
            }
            await self.websocket.send(json.dumps(message))

            # Receive audio response
            while True:
                response = await self.websocket.recv()
                data = json.loads(response)

                # Extract audio data
                if "serverContent" in data:
                    for part in data["serverContent"].get("modelTurn", {}).get(
                        "parts", []
                    ):
                        if "inline_data" in part:
                            audio_data = bytes.fromhex(part["inline_data"]["data"])
                            yield audio_data

                # Check if turn is complete
                if data.get("serverContent", {}).get("turnComplete"):
                    break

        except Exception as e:
            print(f"[Voice] TTS error: {e}")

    async def bidirectional_stream(
        self,
        audio_input: AsyncGenerator[bytes, None],
        on_text_received: Callable[[str], None],
        on_audio_received: Callable[[bytes], None],
    ):
        """
        Handle bidirectional streaming: audio in + audio out simultaneously.

        Args:
            audio_input: Generator yielding input audio chunks
            on_text_received: Callback for transcribed text
            on_audio_received: Callback for output audio
        """
        if not self.websocket:
            await self.connect()

        # Create tasks for sending and receiving
        send_task = asyncio.create_task(self._send_audio(audio_input))
        receive_task = asyncio.create_task(
            self._receive_stream(on_text_received, on_audio_received)
        )

        # Wait for both to complete
        await asyncio.gather(send_task, receive_task)

    async def _send_audio(self, audio_generator: AsyncGenerator[bytes, None]):
        """Send audio chunks to WebSocket."""
        async for chunk in audio_generator:
            message = {
                "realtime_input": {
                    "media_chunks": [{"mime_type": "audio/pcm", "data": chunk.hex()}]
                }
            }
            await self.websocket.send(json.dumps(message))

    async def _receive_stream(
        self,
        on_text: Callable[[str], None],
        on_audio: Callable[[bytes], None],
    ):
        """Receive and process WebSocket messages."""
        async for message in self.websocket:
            data = json.loads(message)

            if "serverContent" in data:
                for part in data["serverContent"].get("modelTurn", {}).get(
                    "parts", []
                ):
                    # Handle text
                    if "text" in part:
                        on_text(part["text"])

                    # Handle audio
                    if "inline_data" in part:
                        audio = bytes.fromhex(part["inline_data"]["data"])
                        on_audio(audio)
