import os
import threading

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
        # Invoke the graph and store the result
        """
        result = graph.invoke({"documentpath": file_path, "questioning_context": content, "n_questions": 3}, debug=True)

        add_notes_from_graph_to_deck(result, 1618431839549)
        sync("Linus")
        # Open the output file in write mode
        with open('output.txt', 'w') as file:
            file.write(str(result))
        """
        return "Not implemented"

    def reset_api_key(self):
        settings_manager.reset_api_key(webview.windows[0])

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
    # TODO Initialize the collection manger somewhere else so you don't get the weakref error. You can't pass it to the api (and don't need to. You just need to call some functions from it.)
    window = webview.create_window("FLASH", entry, maximized=True, js_api=Api())
    if not settings_manager.api_key_exists():
        window.events.loaded += lambda: settings_manager.set_api_key_dialog()
    webview.start(debug=True)

#TODO Initialize somewhere the connection whenever new profile is selected/set in the database => Needs to be used by collection manager