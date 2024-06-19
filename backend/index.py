import os
import threading
from time import time

import webview
from apiUtils.key_manager import api_key_available, set_api_key
from ankiUtils.collection_manager import add_notes_from_graph_to_deck, sync
from agents.note_graph import graph


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
        """
        if BasicNote.valid:
            generation = generate_card(content, BasicNote)
            note = generate_note(BasicNote, generation)
            add_note(1618431839549, note)
            sync("Linus")

        """
        # Invoke the graph and store the result
        result = graph.invoke({"documentpath": "C:\\Users\\linus\\Desktop\\layout_parser.pdf", "questioning_context": "It's a paper on layout parsing. Focus on making short flashcards!", "n_questions": 3}, debug=True)

        add_notes_from_graph_to_deck(result, 1618431839549)
        sync("Linus")
        # Open the output file in write mode
        with open('output.txt', 'w') as file:
            # Write the result to the file
            file.write(str(result))

        """
        basic_note_to_add = {'Type': 'Cloze', 'Text': 'The primary goal of the LayoutParser library in the context of document image analysis is to:\n <ol>\n<li>{{c1::provide a unified toolkit for deep learning-based document image analysis}}</li>\n<li>{{c2::streamline the usage of deep learning models in document image analysis research and applications}}</li>\n<li>{{c3::incorporate a community platform for sharing pre-trained models and full document digitization pipelines}}</li>\n</ol>', 'Back Extra': 'It aims to make it helpful for both lightweight and large-scale digitization pipelines in real-world use cases.'}
        basic_note_to_add = generate_note(basic_note_to_add)
        if basic_note_to_add is not None:
            add_note(1618431839549, basic_note_to_add)
            print("ADDING NOTE")
            sync("Linus")
        else:
            print("Note not added")

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
    #TODO Make debug False
    window = webview.create_window("FLASH", entry, js_api=Api(), maximized=True)
    if not api_key_available():
        window.events.loaded += lambda: set_api_key(window)
    webview.start(debug=True)


