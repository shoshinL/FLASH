import os
import webview
from anki.errors import DBError
from apiUtils.settings_manager import SettingsManager
from agents.note_graph import graph

def custom_alert(message) -> str:
    js_code = f"""
    var alertDiv = document.createElement('div');
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.left = '50%';
    alertDiv.style.transform = 'translateX(-50%)';
    alertDiv.style.backgroundColor = '#f8d7da';
    alertDiv.style.color = '#721c24';
    alertDiv.style.padding = '10px';
    alertDiv.style.borderRadius = '5px';
    alertDiv.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = '{message.replace("'", "\\'")}';
    document.body.appendChild(alertDiv);
    setTimeout(function() {{ alertDiv.remove(); }}, 5000);
    """
    return js_code

def check_settings(window):
    settings = settings_manager.get_settings()
    alert_messages = []
    if not settings['api_key_set']:
        alert_messages.append("Please set your nVidia nim-API key in the settings.")
    if not settings['anki_data_location_valid']:
        alert_messages.append("Please select a valid Anki database file (prefs21.db) in the settings.")
    
    if alert_messages:
        window.evaluate_js(custom_alert("\n".join(alert_messages)))


class Api:
    def select_file(self):
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None

    def make_card(self, content, file_path, card_amount):
        # Example: Using the content and file_path to create a card
        # This is a placeholder and should be implemented based on your specific requirements
        print(f"Content: {content}, File path: {file_path}, Card amount: {card_amount}")
        return "Card creation not implemented"

    def get_settings(self):
        return settings_manager.get_settings()

    def get_profiles(self, anki_db_path):
        profiles = settings_manager.get_profiles(anki_db_path)
        return {"profiles": profiles}

    def get_decks(self, profile):
        decks = settings_manager.get_decks(profile)
        return {"decks": decks}

    def select_file_path(self):
        file_types = ('Database Files (*.db)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and result[0]:
            return settings_manager._upsert_anki_db_path(result[0])
        return {"error": "No file selected"}

    def set_profile(self, profile):
        return settings_manager._upsert_profile(profile)

    def set_deck(self, deck_name):
        settings_manager._upsert_deck_name(deck_name)
        return {"success": True, "deck_name": deck_name}

    def set_api_key(self, api_key):
        success = settings_manager.set_api_key(api_key)
        return {"success": success, "api_key_set": settings_manager.api_key_exists()}

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

def anki_close_dialog(window):
    window.create_confirmation_dialog('NOTICE', f'Please close Anki before restarting FLASH!')
    window.destroy()
    exit(1)

if __name__ == "__main__":
    api = Api()
    window = webview.create_window("FLASH", entry, maximized=True, js_api=api)

    try:
        settings_manager = SettingsManager()
        window.events.loaded += lambda: check_settings(window)
        webview.start(debug=True)
    except DBError:
        webview.start(anki_close_dialog, window)        

    