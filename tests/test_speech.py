import tempfile
import unittest
from pathlib import Path
import wave

from callsign_trainer.speech import SpeechEngine


class SpeechEngineTests(unittest.TestCase):
    @staticmethod
    def _write_clip(path: Path, frames: int = 100) -> None:
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(1_000)
            output.writeframes(bytes(frames * 2))

    def test_build_wav_joins_tokens_with_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset_dir = Path(directory)
            self._write_clip(asset_dir / "A-1.wav")
            self._write_clip(asset_dir / "B-1.wav")
            destination = asset_dir / "phrase.wav"

            engine = SpeechEngine.__new__(SpeechEngine)
            engine._asset_dir = asset_dir
            engine._gap_ms = 90
            engine._build_wav("AB", destination)

            with wave.open(str(destination), "rb") as phrase:
                self.assertEqual(phrase.getnframes(), 290)

    def test_build_wav_uses_selected_speed_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset_dir = Path(directory)
            self._write_clip(asset_dir / "A-1.wav", frames=100)
            self._write_clip(asset_dir / "A-2.wav", frames=250)
            destination = asset_dir / "phrase.wav"

            engine = SpeechEngine.__new__(SpeechEngine)
            engine._asset_dir = asset_dir
            engine._gap_ms = 90
            engine._build_wav("A", destination, speed=2)

            with wave.open(str(destination), "rb") as phrase:
                self.assertEqual(phrase.getnframes(), 250)

    def test_missing_assets_report_generation_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            engine = SpeechEngine(asset_dir=Path(directory))

        self.assertIn("generate_audio_assets", engine.error or "")


if __name__ == "__main__":
    unittest.main()
