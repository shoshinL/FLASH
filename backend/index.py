import os
import threading
import json
import webview
from apiUtils.settings_manager import SettingsManager
from agents.note_graph import graph

settings_manager = SettingsManager()

class Api:
    def select_file(self):
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None

    def make_card(self, content, file_path):
        # Example: Using the content and file_path to create a card
        # This is a placeholder and should be implemented based on your specific requirements
        return "Card creation not implemented"

    def reset_api_key(self):
        settings_manager.reset_api_key(webview.windows[0])
        return {"api_key_set": settings_manager.api_key_exists()}

    def get_settings(self):
        return settings_manager.get_settings()

    def get_profiles(self, anki_db_path):
        profiles = settings_manager.get_profiles(anki_db_path)
        return {"profiles": profiles}

    def get_decks(self, profile):
        decks = settings_manager.get_decks(profile)
        return {"decks": decks}

    def select_file_path(self):
        new_path = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if new_path:
            return settings_manager._upsert_anki_db_path(new_path[0])
        return {"error": "No path selected"}

    def set_profile(self, profile):
        return settings_manager._upsert_profile(profile)

    def set_deck(self, deck_name):
        settings_manager._upsert_deck_name(deck_name)
        return {"success": True, "deck_name": deck_name}

def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists("../gui/index.html"):  # unfrozen development
        return "../gui/index.html"
    if exists("../Resources/gui/index.html"):  # frozen py2app
        return "../Resources/gui/index.html"
    if exists("./gui/index.html"):
        return "./gui/index.html"
    raise Exception("No index.html found")

entry = get_entrypoint()

if __name__ == "__main__":
    api = Api()
    window = webview.create_window("FLASH", entry, maximized=True, js_api=api)
    
    def on_loaded():
        if not settings_manager.api_key_exists():
            settings_manager.reset_api_key(window)

    window.events.loaded += on_loaded
    
    webview.start(debug=True)