from app.schemas.transcription import NoteEvent
from app.services.fretboard_mapper import FretboardMapper


def test_map_notes_returns_positions():
    mapper = FretboardMapper()
    notes = [
        NoteEvent(pitch_midi=64, start_time=0.0, duration=0.5, confidence=0.9),
        NoteEvent(pitch_midi=66, start_time=0.5, duration=0.5, confidence=0.9),
    ]
    mapped = mapper.map_notes(notes)
    assert len(mapped) == 2
    assert all(note.fret >= 0 for note in mapped)
