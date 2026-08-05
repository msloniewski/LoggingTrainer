"""Non-blocking speech output."""

from __future__ import annotations

import queue
import threading


class SpeechEngine:
    def __init__(self, rate: int = 145) -> None:
        self._items: queue.Queue[str | None] = queue.Queue()
        self._rate = rate
        self._error: str | None = None
        threading.Thread(target=self._worker, daemon=True).start()

    @property
    def error(self) -> str | None:
        return self._error

    def say(self, text: str) -> None:
        self._items.put(text)

    def close(self) -> None:
        self._items.put(None)

    def _worker(self) -> None:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
        except Exception as exc:  # platform backends fail in different ways
            self._error = f"Text-to-speech unavailable: {exc}"
            return

        while True:
            text = self._items.get()
            if text is None:
                engine.stop()
                return
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as exc:
                self._error = f"Could not play speech: {exc}"

