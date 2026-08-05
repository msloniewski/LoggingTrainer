from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from .callsigns import callsign_to_phonetics, generate_callsign, normalize_callsign
from .speech import SpeechEngine


class TrainerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Callsign Logging Trainer")
        self.geometry("560x390")
        self.minsize(480, 350)

        self._rng = random.Random()
        self._speech = SpeechEngine()
        self._callsign = ""
        self._region = ""
        self._correct = 0
        self._attempted = 0

        self.answer = tk.StringVar()
        self.status = tk.StringVar(value="Press Start to hear the first callsign.")
        self.score = tk.StringVar(value="Score: 0 / 0")
        self.speed = tk.IntVar(value=145)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Callsign Logging Trainer", font=("TkDefaultFont", 18, "bold")).pack(pady=(0, 18))
        ttk.Label(root, text="Listen, type the callsign, then press Enter.").pack()

        self.entry = ttk.Entry(root, textvariable=self.answer, justify="center", font=("TkFixedFont", 22))
        self.entry.pack(fill="x", pady=18)
        self.entry.bind("<Return>", self._submit)

        buttons = ttk.Frame(root)
        buttons.pack()
        self.start_button = ttk.Button(buttons, text="Start / Next", command=self._next)
        self.start_button.grid(row=0, column=0, padx=5)
        ttk.Button(buttons, text="Repeat (F2)", command=self._repeat).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Check (Enter)", command=self._submit).grid(row=0, column=2, padx=5)
        self.bind("<F2>", lambda _event: self._repeat())

        ttk.Separator(root).pack(fill="x", pady=20)
        ttk.Label(root, textvariable=self.status, anchor="center", wraplength=500).pack(fill="x")
        ttk.Label(root, textvariable=self.score, font=("TkDefaultFont", 12, "bold")).pack(pady=(14, 0))

    def _next(self) -> None:
        self._callsign, self._region = generate_callsign(self._rng)
        self.answer.set("")
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
        self._speech.say(callsign_to_phonetics(self._callsign))

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
        self.score.set(f"Score: {self._correct} / {self._attempted}")
        self.after(1100, self._next)

    def _close(self) -> None:
        self._speech.close()
        self.destroy()


def main() -> None:
    TrainerApp().mainloop()


if __name__ == "__main__":
    main()

