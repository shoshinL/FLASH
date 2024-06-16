from typing import List
from anki.collection import Collection
from .db_access import get_sync_auth

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

def add_note(deck_id: int, note: dict):
    col.add_note(note, deck_id)

#TODO: This should trigger if the window is closed => Implement with hook.
def sync(profile: str):
    col.close_for_full_sync()
    sync_auth = get_sync_auth(profile)
    col.sync_collection(sync_auth, False)