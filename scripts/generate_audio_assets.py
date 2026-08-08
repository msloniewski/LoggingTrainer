"""Generate reusable NATO phonetic WAV files locally with Kokoro."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import wave

from callsign_trainer.callsigns import PHONETICS


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "assets" / "audio"
VARIANT_SPEEDS = (1.0, 1.25, 1.5)


def _asset_name(character: str, word: str, variant: int) -> str:
    if character == "/":
        return f"stroke-{variant}.wav"
    slug = word.lower().replace(" ", "-")
    return f"{character.upper()}-{slug}-{variant}.wav"


def _trim_silence(path: Path, padding_ms: int = 12) -> None:
    trimmed = path.with_name(f"{path.stem}.trimmed.wav")
    padding = padding_ms / 1000
    trim_start = (
        "silenceremove="
        f"start_periods=1:start_duration=0.005:start_threshold=-40dB:start_silence={padding}"
    )
    # Trim the end in reverse so internal pauses are never mistaken for trailing silence.
    audio_filter = f"{trim_start},areverse,{trim_start},areverse"

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(path),
                "-af",
                audio_filter,
                "-ac",
                "1",
                "-ar",
                "24000",
                "-c:a",
                "pcm_s16le",
                str(trimmed),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f"FFmpeg exited with {result.returncode}")

        with wave.open(str(trimmed), "rb") as source:
            params = source.getparams()
        if params.nchannels != 1 or params.sampwidth != 2 or not params.nframes:
            raise ValueError(f"FFmpeg produced an invalid WAV: {params}")
        trimmed.replace(path)
    finally:
        trimmed.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default="am_michael", help="Kokoro voice")
    parser.add_argument("--variants", type=int, default=3, choices=range(1, 4))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true", help="replace existing assets")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg is required to trim generated audio")

    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline

    args.output.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code="a")
    total = sum(len(words) for words in PHONETICS.values()) * args.variants
    generated = 0

    for character, words in PHONETICS.items():
        for word in words:
            for variant in range(1, args.variants + 1):
                destination = args.output / _asset_name(character, word, variant)
                if destination.exists() and not args.force:
                    continue

                print(f"Generating {destination.name} ({generated + 1}/{total})")
                temporary = destination.with_suffix(".tmp.wav")
                try:
                    segments = [
                        audio
                        for _graphemes, _phonemes, audio in pipeline(
                            word,
                            voice=args.voice,
                            speed=VARIANT_SPEEDS[variant - 1],
                        )
                    ]
                    if not segments:
                        raise RuntimeError(f"Kokoro returned no audio for {word}")
                    sf.write(temporary, np.concatenate(segments), 24_000, subtype="PCM_16")
                    _trim_silence(temporary)
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
                generated += 1

    print(f"Generated {generated} file(s) in {args.output}")


if __name__ == "__main__":
    main()
