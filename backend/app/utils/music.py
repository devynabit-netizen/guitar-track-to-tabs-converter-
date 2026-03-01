"""Music utility helpers."""
PITCHES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def note_name_to_midi(note: str) -> int:
    name = note[:-1]
    octave = int(note[-1])
    return 12 * (octave + 1) + PITCHES[name]


def midi_to_hz(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12))


def quantize_time(seconds: float, bpm: float, division: int = 16) -> float:
    beat = 60 / bpm
    grid = beat * (4 / division)
    return round(seconds / grid) * grid


def confidence_from_velocity(velocity: float) -> float:
    return max(0.0, min(1.0, velocity / 127.0 if velocity else 0.8))
