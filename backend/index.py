import json
import os
import random
import time
import webview
import logging
import sys
from anki.errors import DBError

from settingUtils.settings_manager import SettingsManager
from settingUtils.settings_context import SettingsContext
from agents.note_graph import graph

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)


def custom_alert(messages, display_duration=7000) -> str:
    # Convert messages list into a JSON string to handle special characters and maintain structure
    messages_json = json.dumps(messages)
    js_code = f"""
    var messages = {messages_json};
    messages.forEach(function(message, index) {{
        var alertDiv = document.createElement('div');
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = (20 + 60 * index) + 'px'; // Offset each alert
        alertDiv.style.left = '50%';
        alertDiv.style.transform = 'translateX(-50%)';
        alertDiv.style.backgroundColor = '#f8d7da';
        alertDiv.style.color = '#721c24';
        alertDiv.style.padding = '10px';
        alertDiv.style.borderRadius = '5px';
        alertDiv.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        alertDiv.style.zIndex = '10000' + index; // Ensure each alert is above the previous
        alertDiv.innerHTML = message;
        document.body.appendChild(alertDiv);
        setTimeout(function() {{ alertDiv.remove(); }}, {display_duration} + 1000 * index); // Staggered removal
    }});
    """
    return js_code

def check_settings(window):
    settings = SettingsContext.get_settings_manager().get_settings()
    alert_messages = []
    if not settings['api_key_set']:
        alert_messages.append("Please set your nVidia nim-API key in the settings.")
    if not settings['anki_data_location_valid']:
        alert_messages.append("Please select a valid Anki database file (prefs21.db) in the settings.")
    
    if alert_messages:
        window.evaluate_js(custom_alert(alert_messages, 7000))
        return False

    return True


class Api:
    def show_alert(self, message):
        webview.windows[0].evaluate_js(custom_alert([message], 7000))

    def valid_settings(self):
        return check_settings(webview.windows[0])

    def select_file(self):
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None
        
    def generate_flashcards_test(self, content, file_path, card_amount):
            def generate_updates():
                total_steps = 5
                flashcard_types = ['Basic', 'Basic (and reversed card)', 'Basic (type in the answer)', 'Cloze']
                
                for step in range(1, total_steps + 1):
                    progress = (step / total_steps) * 100
                    if step == 1:
                        yield {"progress": progress, "message": "Processing document..."}
                    elif step == 2:
                        yield {"progress": progress, "message": "Analyzing content..."}
                    elif step == 3:
                        yield {"progress": progress, "message": "Generating flashcards..."}
                    elif step == 4:
                        yield {"progress": progress, "message": "Finalizing results..."}
                    else:
                        flashcards = []
                        for i in range(1, int(card_amount) + 1):
                            card_type = random.choice(flashcard_types)
                            if card_type == 'Basic':
                                flashcards.append({
                                    "Type": "Basic",
                                    "Front": f"Question {i} from {content}",
                                    "Back": f"Answer {i} for {file_path}"
                                })
                            elif card_type == 'Basic (and reversed card)':
                                flashcards.append({
                                    "Type": "Basic (and reversed card)",
                                    "Front": f"Term {i} from {content}",
                                    "Back": f"Definition {i} for {file_path}"
                                })
                            elif card_type == 'Basic (type in the answer)':
                                flashcards.append({
                                    "Type": "Basic (type in the answer)",
                                    "Front": f"Type the answer for Question {i} from {content}",
                                    "Back": f"Answer{i}"
                                })
                            elif card_type == 'Cloze':
                                flashcards.append({
                                    "Type": "Cloze",
                                    "Text": f"{{{{c1::{content}}}}} is related to {{{{c2::{file_path}}}}} in concept {i}",
                                    "BackExtra": f"Additional info for concept {i}"
                                })
                        
                        results = {"flashcards": flashcards, "filename": os.path.basename(file_path)}
                        yield {"progress": progress, "message": "Complete!", "result": results}
                    
                    time.sleep(1)  # Simulate processing time

            for update in generate_updates():
                webview.windows[0].evaluate_js(f"window.dispatchEvent(new CustomEvent('backendUpdate', {{detail: {json.dumps(update)}}}));")
            
            return "Flashcard generation test completed"

    def generate_flashcards(self, content, file_path, card_amount):
        last_step = ""
        progress = 0

        for state in graph.stream({"questioning_context": content, "documentpath": file_path, "n_questions": card_amount}):
            key = next(iter(state))
            try:
                current_step = state[key]["current_step"]
            except:
                continue

            if current_step != last_step:
                logger.debug(f"Current step in graph: {current_step}")
                last_step = current_step
                progress += 20
                update = {"progress": progress, "message": current_step}
                if current_step == "Finished!":
                    flashcards = state[key]["notes"]
                    filename = os.path.basename(state[key]["documentpath"])
                    update = {
                        "progress": 100,
                        "message": "Complete!",
                        "result": {"flashcards":flashcards, "filename":filename}
                    }
                webview.windows[0].evaluate_js(f"window.dispatchEvent(new CustomEvent('backendUpdate', {{detail: {json.dumps(update)}}}));")

        return "Flashcard generation completed"

    def save_accepted_flashcards(self, flashcards, filename):
        if not flashcards:
            return "ERROR"
        try:
            settings_manager.add_generated_cards_to_deck(filename, flashcards)
            return "Success!!"
        except Exception as e:
            print(f"Error saving flashcards: {e}")
            return "ERROR"

    def get_settings(self):
        return SettingsContext.get_settings_manager().get_settings()

    def get_profiles(self, anki_db_path):
        profiles = SettingsContext.get_settings_manager().get_profiles(anki_db_path)
        return {"profiles": profiles}

    def get_decks(self, profile):
        decks = SettingsContext.get_settings_manager().get_decks(profile)
        return {"decks": decks}
    
    def get_selected_deck(self):
        return SettingsContext.get_settings_manager().deck_name
    
    def get_selected_profile(self):
        return SettingsContext.get_settings_manager().profile

    def select_file_path(self):
        file_types = ('Database Files (*.db)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and result[0]:
            return SettingsContext.get_settings_manager().upsert_anki_db_path(result[0])
        return {"error": "No file selected"}

    def set_profile(self, profile):
        return SettingsContext.get_settings_manager().upsert_profile(profile)

    def set_deck(self, deck_name):
        SettingsContext.get_settings_manager().upsert_deck_name(deck_name)
        return {"success": True, "deck_name": deck_name}

    def set_api_key(self, api_key):
        success = SettingsContext.get_settings_manager().set_api_key(api_key)
        return {"success": success, "api_key_set": SettingsContext.get_settings_manager().api_key_exists()}


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
    logging.debug("Starting application")
    api = Api()
    window = webview.create_window("FLASH", entry, maximized=True, js_api=api)

    try:
        logging.debug("Initializing SettingsManager")
        settings_manager = SettingsManager()
        SettingsContext.set_settings_manager(settings_manager)
        logging.debug("SettingsManager initialized successfully")
        window.events.loaded += lambda: check_settings(window)
        logging.debug("Starting webview")
        webview.start()
    except DBError as e:
        logging.error(f"DBError occurred: {str(e)}")
        webview.start(anki_close_dialog, window)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")

    