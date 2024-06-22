import os
from typing import Dict, List
from anki.collection import Collection
from anki.sync import SyncAuth
from anki.notes import Note

class AnkiCollectionManager:
    sync_auth = SyncAuth
    col = Collection

    def __init__(self, profile_path: str, sync_auth: SyncAuth):
        self.sync_auth = sync_auth
        self.col = Collection(os.path.join(profile_path, "collection.anki2"))

    def get_decks(self) -> Dict[str, int]:
        decks = self.col.decks.all_names_and_ids()
        return {deck.name: deck.id for deck in decks}

    """
    not used right now
    def add_new_deck(self, deck_name: str):
        self.col.add_normal_deck_with_name(deck_name)
    """

    def _get_model_id(self, name: str):
        return self.col.models.id_for_name(name)

    def _get_model(self, model_id: int) -> Dict:
        return self.col.models.get(model_id)

    def _get_model_fields(self, model: Dict) -> List[str]:
        return self.col.models.field_names(model)

    def _generate_note(self, generated_note: dict, filename: str) -> Note:
        id = self.get_model_id(generated_note["Type"])
        model = self.get_model(id)
        note = Note(self.col, model)

        fields = self.get_model_fields(model)

        #validate that the generated note matches the model
        for field in fields:
            if field not in generated_note.keys():
                return None

        for field in fields:
            note.__setitem__(field, generated_note[field])

        note.add_tag(f"FLASH_from_{filename}")
        return note

    def _add_note(self, deck_id: int, note: Note) -> None:
        self.col.add_note(note, deck_id)

    def add_notes_from_graph_to_deck(self, graphState: Dict, deck_id: int) -> None:
        documentpath = graphState["documentpath"]
        filename = os.path.basename(documentpath)
        notes = graphState["notes"]

        for note in notes:
            note = self.generate_note(note, filename)
            if note is not None:
                self.add_note(deck_id, note)

    #TODO: This should trigger if the window is closed => Implement with hook.
    def sync(self):
        self.col.close_for_full_sync()
        self.col.sync_collection(self.sync_auth, False)