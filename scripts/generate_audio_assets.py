"""Generate reusable NATO phonetic WAV files locally with Kokoro."""

from __future__ import annotations

import argparse
from array import array
from pathlib import Path
import sys
import wave

from callsign_trainer.callsigns import PHONETIC


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "assets" / "audio"
VARIANT_SPEEDS = (1.08, 1.15, 1.02)


def _asset_name(character: str, variant: int) -> str:
    token = "stroke" if character == "/" else character.upper()
    return f"{token}-{variant}.wav"


def _trim_silence(path: Path, padding_ms: int = 45) -> None:
    with wave.open(str(path), "rb") as source:
        params = source.getparams()
        frames = source.readframes(params.nframes)

    if params.nchannels != 1 or params.sampwidth != 2 or not frames:
        raise ValueError(f"Expected 16-bit mono PCM WAV from Kokoro, got {params}")

    samples = array("h")
    samples.frombytes(frames)
    if sys.byteorder != "little":
        samples.byteswap()

    peak = max(abs(sample) for sample in samples)
    threshold = max(250, int(peak * 0.025))
    audible = [index for index, sample in enumerate(samples) if abs(sample) >= threshold]
    if not audible:
        raise ValueError(f"Generated audio is silent: {path}")

    padding = params.framerate * padding_ms // 1000
    start = max(0, audible[0] - padding)
    end = min(len(samples), audible[-1] + padding + 1)
    trimmed = samples[start:end]
    if sys.byteorder != "little":
        trimmed.byteswap()

    with wave.open(str(path), "wb") as destination:
        destination.setparams(params._replace(nframes=0))
        destination.writeframes(trimmed.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default="af_heart", help="Kokoro voice")
    parser.add_argument("--variants", type=int, default=3, choices=range(1, 4))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true", help="replace existing assets")
    args = parser.parse_args()

    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline

    args.output.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code="a")
    total = len(PHONETIC) * args.variants
    generated = 0

    for character, word in PHONETIC.items():
        for variant in range(1, args.variants + 1):
            destination = args.output / _asset_name(character, variant)
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
