"""Non-blocking playback assembled from recorded phonetic tokens."""

from __future__ import annotations

import os
from pathlib import Path
import queue
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import wave


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "audio"


class SpeechEngine:
    def __init__(self, gap_ms: int = 90, asset_dir: Path = ASSET_DIR) -> None:
        self._items: queue.Queue[str | None] = queue.Queue()
        self._gap_ms = gap_ms
        self._asset_dir = asset_dir
        self._error = self._validate()
        if self._error is None:
            threading.Thread(target=self._worker, daemon=True).start()

    @property
    def error(self) -> str | None:
        return self._error

    def say(self, callsign: str) -> None:
        self._items.put(callsign)

    def close(self) -> None:
        if self._error is None:
            self._items.put(None)

    def _validate(self) -> str | None:
        missing = [token for token in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" if not self._clips(token)]
        if not self._clips("/"):
            missing.append("/")
        if missing:
            return "Audio assets are missing. Run: python -m scripts.generate_audio_assets"
        if sys.platform == "win32":
            return None
        if not any(shutil.which(player) for player in self._player_names()):
            return "No WAV player found (install paplay, aplay, or afplay)."
        return None

    def _clips(self, character: str) -> tuple[Path, ...]:
        token = "stroke" if character == "/" else character.upper()
        return tuple(sorted(self._asset_dir.glob(f"{token}-*.wav")))

    @staticmethod
    def _player_names() -> tuple[str, ...]:
        if sys.platform == "darwin":
            return ("afplay",)
        return ("paplay", "aplay")

    def _build_wav(self, callsign: str, destination: Path) -> None:
        clips = [random.choice(self._clips(character)) for character in callsign.upper()]
        params = None
        chunks: list[bytes] = []

        for clip in clips:
            with wave.open(str(clip), "rb") as source:
                clip_params = source.getparams()
                if params is None:
                    params = clip_params
                elif (
                    clip_params.nchannels,
                    clip_params.sampwidth,
                    clip_params.framerate,
                    clip_params.comptype,
                ) != (
                    params.nchannels,
                    params.sampwidth,
                    params.framerate,
                    params.comptype,
                ):
                    raise ValueError(f"Audio format does not match: {clip}")
                chunks.append(source.readframes(clip_params.nframes))

        assert params is not None
        gap_frames = params.framerate * self._gap_ms // 1000
        silence = bytes(gap_frames * params.nchannels * params.sampwidth)
        with wave.open(str(destination), "wb") as output:
            output.setparams(params._replace(nframes=0))
            output.writeframes(silence.join(chunks))

    def _play(self, path: Path) -> None:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME)
            return

        player = next(name for name in self._player_names() if shutil.which(name))
        result = subprocess.run(
            [player, str(path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f"{player} exited with {result.returncode}")

    def _worker(self) -> None:
        while True:
            callsign = self._items.get()
            if callsign is None:
                return

            path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporary:
                    path = Path(temporary.name)
                self._build_wav(callsign, path)
                self._play(path)
            except Exception as exc:
                self._error = f"Could not play speech: {exc}"
            finally:
                if path is not None:
                    path.unlink(missing_ok=True)
