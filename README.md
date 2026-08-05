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

Linux speech may also require a system speech backend such as eSpeak NG:

```bash
sudo apt install python3-tk espeak-ng libespeak1
```

Keyboard controls: Enter checks an answer and F2 repeats the callsign.

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
