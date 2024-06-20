import os
import threading

import webview
from apiUtils.key_manager import api_key_available, set_api_key
from ankiUtils.collection_manager import add_notes_from_graph_to_deck, sync
from agents.note_graph import graph


class Api:

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def select_file(self):
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, "w") as f:
            f.write(content)
    
    def reset_api_key(self):
        set_api_key(webview.windows[0])

    def make_card(self, content, file_path):
        # Example: Using the content and file_path to create a card
        print("Content:", content)
        print("File Path:", file_path)
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

    def ls(self):
        return os.listdir(".")


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


def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped

        return wrapper

    return decorator


entry = get_entrypoint()

if __name__ == "__main__":
    window = webview.create_window("FLASH", entry, js_api=Api(), maximized=True)
    if not api_key_available():
        window.events.loaded += lambda: set_api_key(window)
    webview.start(debug=True)
