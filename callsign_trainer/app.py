from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from .callsigns import generate_callsign, normalize_callsign
from .speech import DEFAULT_VOICE, SPEEDS, VOICES, SpeechEngine


class TrainerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Callsign Logging Trainer")
        self.geometry("560x500")
        self.minsize(480, 470)

        self._rng = random.Random()
        self._speech = SpeechEngine()
        self._callsign = ""
        self._region = ""
        self._correct = 0
        self._attempted = 0

        self.answer = tk.StringVar()
        self.status = tk.StringVar(value="Press Enter to hear the first callsign.")
        self.score = tk.StringVar(value="Correct: 0    Questions: 0")
        self.speed = tk.IntVar(value=1)
        self.voice = tk.StringVar(value=DEFAULT_VOICE)

        self._build_ui()
        self.entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Callsign Logging Trainer", font=("TkDefaultFont", 18, "bold")).pack(pady=(0, 18))
        ttk.Label(root, text="Listen, type the callsign, then press Enter.").pack()

        self.entry = ttk.Entry(root, textvariable=self.answer, justify="center", font=("TkFixedFont", 22))
        self.entry.pack(fill="x", pady=18)
        self.bind("<Return>", self._submit)

        buttons = ttk.Frame(root)
        buttons.pack()
        self.start_button = ttk.Button(buttons, text="Next", command=self._next)
        self.start_button.grid(row=0, column=0, padx=5)
        ttk.Button(buttons, text="Repeat (F2)", command=self._repeat).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Check (Enter)", command=self._submit).grid(row=0, column=2, padx=5)
        self.bind("<F2>", lambda _event: self._repeat())

        speeds = ttk.LabelFrame(root, text="Voice speed", padding=(12, 6))
        speeds.pack(pady=(18, 0))
        for column, (label, variant) in enumerate(SPEEDS):
            ttk.Radiobutton(speeds, text=label, variable=self.speed, value=variant).grid(
                row=0, column=column, padx=8
            )

        voices = ttk.LabelFrame(root, text="Voice", padding=(12, 6))
        voices.pack(pady=(12, 0))
        for column, (label, voice) in enumerate(VOICES):
            ttk.Radiobutton(voices, text=label, variable=self.voice, value=voice).grid(
                row=0, column=column, padx=8
            )

        ttk.Separator(root).pack(fill="x", pady=20)
        ttk.Label(root, textvariable=self.score, font=("TkDefaultFont", 12, "bold")).pack(pady=(0, 14))
        ttk.Label(root, textvariable=self.status, anchor="center", wraplength=500).pack(fill="x")

    def _next(self, preserve_status: bool = False) -> None:
        self._callsign, self._region = generate_callsign(self._rng)
        self.answer.set("")
        if not preserve_status:
            self.status.set("Listening…")
        self.entry.focus_set()
        self._repeat()

    def _repeat(self) -> None:
        if not self._callsign:
            self._next()
            return
        if self._speech.error:
            self.status.set(self._speech.error)
            return
        self._speech.say(self._callsign, self.speed.get(), self.voice.get())

    def _submit(self, _event: object | None = None) -> None:
        if not self._callsign:
            self._next()
            return
        entered = normalize_callsign(self.answer.get())
        if not entered:
            self.status.set("Type the callsign you heard.")
            return

        self._attempted += 1
        if entered == self._callsign:
            self._correct += 1
            self.status.set(f"Correct — {self._callsign} ({self._region})")
        else:
            self.status.set(f"Not quite — you typed {entered}; correct was {self._callsign} ({self._region})")
        self.score.set(f"Correct: {self._correct}    Questions: {self._attempted}")
        self.after(1100, lambda: self._next(preserve_status=True))

    def _close(self) -> None:
        self._speech.close()
        self.destroy()


def main() -> None:
    TrainerApp().mainloop()


if __name__ == "__main__":
    main()
