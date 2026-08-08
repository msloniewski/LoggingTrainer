import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
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
            self._write_clip(asset_dir / "A-alpha-1.wav")
            self._write_clip(asset_dir / "B-bravo-1.wav")
            destination = asset_dir / "phrase.wav"

            engine = SpeechEngine.__new__(SpeechEngine)
            engine._asset_dir = asset_dir
            engine._gap_ms = 90
            engine._build_wav("AB", destination, pronunciations={"A": "Alpha", "B": "Bravo"})

            with wave.open(str(destination), "rb") as phrase:
                self.assertEqual(phrase.getnframes(), 290)

    def test_build_wav_uses_selected_speed_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset_dir = Path(directory)
            self._write_clip(asset_dir / "A-alpha-1.wav", frames=100)
            self._write_clip(asset_dir / "A-alpha-2.wav", frames=250)
            destination = asset_dir / "phrase.wav"

            engine = SpeechEngine.__new__(SpeechEngine)
            engine._asset_dir = asset_dir
            engine._gap_ms = 90
            engine._build_wav("A", destination, speed=2, pronunciations={"A": "Alpha"})

            with wave.open(str(destination), "rb") as phrase:
                self.assertEqual(phrase.getnframes(), 250)

    def test_repeated_letter_uses_the_same_phonetic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset_dir = Path(directory)
            self._write_clip(asset_dir / "M-mike-1.wav", frames=100)
            self._write_clip(asset_dir / "M-mexico-1.wav", frames=200)
            destination = asset_dir / "phrase.wav"

            engine = SpeechEngine.__new__(SpeechEngine)
            engine._asset_dir = asset_dir
            engine._gap_ms = 90
            with (
                patch("callsign_trainer.speech.random.random", return_value=0.1),
                patch("callsign_trainer.speech.random.choice", return_value="Mexico") as choice,
            ):
                engine._build_wav("MM", destination)

            choice.assert_called_once()
            with wave.open(str(destination), "rb") as phrase:
                self.assertEqual(phrase.getnframes(), 490)

    def test_nato_phonetics_are_used_eighty_percent_of_the_time(self) -> None:
        with patch("callsign_trainer.speech.random.random", return_value=0.2):
            pronunciations = SpeechEngine._choose_pronunciations("M")

        self.assertEqual(pronunciations["M"], "Mike")

    def test_missing_assets_report_generation_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            engine = SpeechEngine(asset_dir=Path(directory))

        self.assertIn("generate_audio_assets", engine.error or "")


if __name__ == "__main__":
    unittest.main()
