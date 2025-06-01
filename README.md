# Midi2FF7R

**Midi2FF7R** is a simple Python script to map MIDI inputs to keystrokes that support the piano minigame of Final Fantasy 7 Rebirth.
First 3 octave keys are assigned to the left hand, the remaining 3 to the right.

---

## 🚀 Features

- Real-time MIDI input handling
- Simulates keyboard/controller input using `pydirectinput`
- Supports octave switching
- Supports semitone switching

---

## 📦 Requirements

This script depends on two Python libraries:

- [`python-rtmidi`](https://pypi.org/project/python-rtmidi/)
- [`pydirectinput-rgx`](https://pypi.org/project/pydirectinput-rgx/)

Install them via pip:

```bash
pip install python-rtmidi pydirectinput-rgx
```

Run the script with:

```bash
python Midi2FFR.py
```
