# Callsign Logging Trainer

A small cross-platform GUI for practising contest callsign copy. It generates
plausible callsigns from representative worldwide amateur prefixes, reads them
with NATO phonetics, and checks the typed answer.

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

Keyboard controls: Enter checks an answer and F2 repeats the callsign. Use the
Normal, Fast, and Super Fast controls to change the delivery speed.

## Audio assets

The trainer assembles callsigns from pre-generated NATO phonetic WAV files in
`assets/audio`. Generate or replace them locally with Kokoro:

```bash
./run.sh --generate-audio
```

The first run uses `uv` to create a Python 3.12 `.venv-kokoro`, installs Kokoro,
and downloads its voice model. The generator uses Michael (`am_michael`) by
default and creates normal, fast, and super-fast versions of each letter, digit,
and the word `stroke`. Existing files are skipped; pass `--force` to regenerate
them with Michael. Audio generation uses FFmpeg to trim silence from each clip,
and Kokoro English generation requires eSpeak NG. On Debian/Ubuntu install both
with `sudo apt install ffmpeg espeak-ng`.

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
