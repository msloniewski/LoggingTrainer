"""Non-blocking playback assembled from recorded phonetic tokens."""

from __future__ import annotations

from pathlib import Path
import queue
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import wave

from .callsigns import PHONETICS


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "audio"
SPEEDS = (("Normal", 1), ("Fast", 2), ("Super Fast", 3))
SPEED_VARIANTS = {variant for _label, variant in SPEEDS}
VOICES = (("Male (Michael)", "am_michael"), ("Female (Heart)", "af_heart"))
DEFAULT_VOICE = VOICES[0][1]
VOICE_IDS = {voice for _label, voice in VOICES}
ALTERNATIVE_PHONETIC_CHANCE = 0.2


class SpeechEngine:
    def __init__(self, gap_ms: int = 35, asset_dir: Path = ASSET_DIR) -> None:
        self._items: queue.Queue[tuple[str, int, str, dict[str, str]] | None] = queue.Queue()
        self._gap_ms = gap_ms
        self._asset_dir = asset_dir
        self._last_callsign = ""
        self._pronunciations: dict[str, str] = {}
        self._error = self._validate()
        if self._error is None:
            threading.Thread(target=self._worker, daemon=True).start()

    @property
    def error(self) -> str | None:
        return self._error

    def say(self, callsign: str, speed: int = 1, voice: str = DEFAULT_VOICE) -> None:
        if speed not in SPEED_VARIANTS:
            raise ValueError(f"Unknown speech speed: {speed}")
        if voice not in VOICE_IDS:
            raise ValueError(f"Unknown voice: {voice}")
        if callsign != self._last_callsign:
            self._last_callsign = callsign
            self._pronunciations = self._choose_pronunciations(callsign)
        self._items.put((callsign, speed, voice, self._pronunciations))

    def close(self) -> None:
        if self._error is None:
            self._items.put(None)

    def _validate(self) -> str | None:
        missing = [
            f"{word} ({label})"
            for character, words in PHONETICS.items()
            for word in words
            for label, variant in SPEEDS
            for _voice_label, voice in VOICES
            if not self._clip(character, word, variant, voice).exists()
        ]
        if missing:
            return "Audio assets are missing. Run: python -m scripts.generate_audio_assets"
        if sys.platform == "win32":
            return None
        if not any(shutil.which(player) for player in self._player_names()):
            return "No WAV player found (install paplay, aplay, or afplay)."
        return None

    def _clip(
        self, character: str, word: str, speed: int, voice: str = DEFAULT_VOICE
    ) -> Path:
        asset_dir = self._asset_dir if voice == DEFAULT_VOICE else self._asset_dir / voice
        if character == "/":
            return asset_dir / f"stroke-{speed}.wav"
        slug = word.lower().replace(" ", "-")
        return asset_dir / f"{character.upper()}-{slug}-{speed}.wav"

    @staticmethod
    def _choose_pronunciations(callsign: str) -> dict[str, str]:
        pronunciations = {}
        for character in dict.fromkeys(callsign.upper()):
            words = PHONETICS[character]
            if len(words) > 1 and random.random() < ALTERNATIVE_PHONETIC_CHANCE:
                pronunciations[character] = random.choice(words[1:])
            else:
                pronunciations[character] = words[0]
        return pronunciations

    @staticmethod
    def _player_names() -> tuple[str, ...]:
        if sys.platform == "darwin":
            return ("afplay",)
        return ("paplay", "aplay")

    def _build_wav(
        self,
        callsign: str,
        destination: Path,
        speed: int = 1,
        pronunciations: dict[str, str] | None = None,
        voice: str = DEFAULT_VOICE,
    ) -> None:
        pronunciations = pronunciations or self._choose_pronunciations(callsign)
        clips = [
            self._clip(character, pronunciations[character], speed, voice)
            for character in callsign.upper()
        ]
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
            item = self._items.get()
            if item is None:
                return
            callsign, speed, voice, pronunciations = item

            path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporary:
                    path = Path(temporary.name)
                self._build_wav(
                    callsign,
                    path,
                    speed=speed,
                    pronunciations=pronunciations,
                    voice=voice,
                )
                self._play(path)
            except Exception as exc:
                self._error = f"Could not play speech: {exc}"
            finally:
                if path is not None:
                    path.unlink(missing_ok=True)
