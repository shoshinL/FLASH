import os
from typing import Dict, List
from anki.collection import Collection
from .db_access import get_sync_auth
from anki.notes import Note

col = Collection("C:\\Users\\linus\\AppData\\Roaming\\Anki2\\Linus\\collection.anki2")
#TODO: Über API holen

def get_decks():
    decks = col.decks.all_names_and_ids()
    return {deck.name: deck.id for deck in decks if deck.name != 'Default'}

def add_new_deck(deck_name: str):
    col.add_normal_deck_with_name(deck_name)

def get_model_id(name: str):
    return col.models.id_for_name(name)

def get_model(model_id: int):
    return col.models.get(model_id)

def get_model_fields(model_id: int) -> List[str]:
    return col.models.field_names(col.models.get(model_id))

def generate_note(generated_note: dict, filename: str) -> Note:
    id = get_model_id(generated_note["Type"])
    model = get_model(id)
    note = Note(col, model)

    fields = get_model_fields(id)

    #validate that the generated note matches the model
    for field in fields:
        if field not in generated_note.keys():
            print(f"Field: {field} not in generated note {generated_note}")
            return None

    for field in fields:
        note.__setitem__(field, generated_note[field])

    note.add_tag(f"FLASH_for_anki_from_{filename}")
    return note

def add_note(deck_id: int, note: Note) -> None:
    col.add_note(note, deck_id)

def add_notes_from_graph_to_deck(graphState, deck_id: int) -> None:
    documentpath = graphState["documentpath"]
    filename = os.path.basename(documentpath)
    notes = graphState["notes"]

    for note in notes:
        note = generate_note(note, filename)
        if note is not None:
            add_note(deck_id, note)

#TODO: This should trigger if the window is closed => Implement with hook.
def sync(profile: str):
    col.close_for_full_sync()
    sync_auth = get_sync_auth(profile)
    col.sync_collection(sync_auth, False)