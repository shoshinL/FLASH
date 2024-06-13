from anki.collection import Collection

def get_deck_due_tree():
    col = Collection("/mnt/c/Users/linus/AppData/Roaming/Anki2/Linus/collection.anki2")
    #col = Collection("C:\Users\linus\AppData\Roaming\Anki2\Linus\collection.anki2")
    deck_due_tree = col.sched.deck_due_tree()
    return deck_due_tree