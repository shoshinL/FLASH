from anki.notes import Note
from anki.collection import Collection
from .note_models import NoteModel
from .collection_manager import get_model_id, col

def generate_note(model: NoteModel, fields: dict) -> Note:
    note = Note(col, model.anki_id)
    for field, value in fields.items():
        note.__setitem__(field, value)
    return note

def add_note(deck_id: int, note: Note) -> None:
    col.add_note(note, deck_id)