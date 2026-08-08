# Callsign Logging Trainer

A small cross-platform GUI for practising contest callsign copy. It generates
plausible callsigns from representative worldwide amateur prefixes, reads them
with NATO and common contest phonetics, and checks the typed answer.

## Run

Python 3.10+ is recommended. Tkinter is included with normal Windows and macOS
Python installations; on Debian/Ubuntu install `python3-tk` if necessary.

```bash
./run.sh
```

The launcher creates `.venv` when needed, installs the dependencies, and starts
the trainer. Set `PYTHON` to choose the Python executable used to create the
environment, for example `PYTHON=python3.12 ./run.sh`.

Linux audio playback requires PulseAudio's `paplay` or ALSA's `aplay`:

```bash
sudo apt install python3-tk pulseaudio-utils
```

Keyboard controls: Enter starts the first question and checks an answer; F2
repeats the callsign. Use the controls to change the delivery speed and switch
between the male Michael and female Heart voices.

## Audio assets

The trainer assembles callsigns from pre-generated NATO phonetic WAV files in
`assets/audio`. Generate or replace them locally with Kokoro:

```bash
./run.sh --generate-audio
```

The first run uses `uv` to create a Python 3.12 `.venv-kokoro`, installs Kokoro,
and downloads its voice model. The generator creates Michael (`am_michael`) and
Heart (`af_heart`) voices, with normal, fast, and super-fast versions of each
NATO or contest phonetic, digit, and the word `stroke`. Existing files are
skipped; pass `--force` to regenerate them. To generate only one voice, pass
`--voice am_michael` or `--voice af_heart`. Audio generation uses FFmpeg to trim
silence from each clip, and Kokoro English generation requires eSpeak NG. On
Debian/Ubuntu install both with `sudo apt install ffmpeg espeak-ng`.

The included voice assets are AI-generated.

## Current scope

The generator creates plausible training calls, but it is not a complete ITU or
national licensing validator. A later version can add weighted real-world prefix
data, portable suffixes, speed/noise controls, CW audio, statistics, and contest
exchange practice. Speech is behind a small adapter so an online high-quality
voice can be added without changing the GUI.

## Test

```bash
python -m unittest discover -v
```

## Windows executable

The `Build Windows executable` GitHub Actions workflow can be run manually or
by pushing a tag beginning with `v`. It generates all audio on Linux, transfers
only the finished WAV files to a Windows runner, and publishes
`LoggingTrainer-windows` as a downloadable workflow artifact. For `v*` tags,
it also creates a GitHub release with `LoggingTrainer.exe` attached.

The packaged `LoggingTrainer.exe` includes the audio and does not include or
require Kokoro, Torch, FFmpeg, eSpeak NG, or Python at runtime.
