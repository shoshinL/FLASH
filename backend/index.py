import os
import threading
from time import time

import webview
from ankiUtils.ankitest import get_deck_due_tree
from apiUtils.key_manager import api_key_exists, set_api_key, get_api_key


class Api:

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, "w") as f:
            f.write(content)
    
    def get_anki_deck(self):
        return str(get_deck_due_tree())

    # TODO implement function
    def make_card(self, content):
        return content

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
    if not api_key_exists():
        window.events.loaded += lambda: set_api_key(window)
    webview.start(debug=True)


