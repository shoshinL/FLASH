import os
import threading
from time import time

import webview
from apiUtils.key_manager import api_key_available, set_api_key
from agents.agenttest import generate_card
from ankiUtils.note_models import BasicNote
from ankiUtils.collection_manager import sync, generate_note, add_note


class Api:

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, "w") as f:
            f.write(content)
    
    def reset_api_key(self):
        set_api_key(webview.windows[0])

    # TODO implement function
    def make_card(self, content):
        if BasicNote.valid:
            generation = generate_card(content, BasicNote)
            note = generate_note(BasicNote, generation)
            add_note(1618431839549, note)
            sync("Linus")
        
        return generation

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
    #TODO Make debug False
    window = webview.create_window("FLASH", entry, js_api=Api())
    if not api_key_available():
        window.events.loaded += lambda: set_api_key(window)
    webview.start(debug=True)


